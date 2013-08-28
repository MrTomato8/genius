from django.db import models

from oscar.apps.basket.abstract_models import (
    AbstractBasket, AbstractLine, AbstractLineAttribute)

from apps.options.models import OptionChoice, ArtworkItem
from apps.options.calc import OptionsCalculator, PriceNotAvailable
import json
from decimal import Decimal
from oscar.templatetags.currency_filters import currency
from django.utils.translation import ugettext as _
from apps.options import utils
from apps.partner.models import StockRecordForChoices
from apps.globals.models import get_tax_percent
from apps.partner.wrappers import DefaultWrapper
import uuid
from django.conf import settings
from apps.basket.exceptions import ItemsRequiredException
Option = models.get_model('catalogue', 'Option')

class Line(AbstractLine):
    PRODUCT_STOCKRECORD, OPTIONS_CALCULATOR = (
        'stockrecord', 'optionscalc')
    STOCKRECORD_SOURCE_CHOICES = (
        (PRODUCT_STOCKRECORD, 'Product stockrecord'),
        (OPTIONS_CALCULATOR, 'Options calculator'))

    # Selector used in overriden _get_stockrecord_property
    # For classic products use PRODUCT_STOCKRECORD
    # For dynamically priced products use OPTIONS_CALCULATOR
    stockrecord_source = models.CharField(
        'Stockrecord source', max_length=30, default=PRODUCT_STOCKRECORD,
        choices=STOCKRECORD_SOURCE_CHOICES)

    # Total items required, nr of stickers or nr of business cards for example
    # making this field nullable an exception will raise if there are problems 
    items_required = models.PositiveIntegerField(null=True)
    def get_option_choices(self):
        choice_data = {}
        choices = []
        itemsperpack = Option.objects.get(code=settings.OPTION_ITEMSPERPACK)
        for attr in self.attributes.exclude(option=itemsperpack):
            # May be a lot of exceptions here, but it will mean problems in
            # another parts of the code or hacking attempt.
            choices.append(OptionChoice.objects.get(option=attr.option,
                                                    code=attr.value_code))
            try:
                data = json.loads(attr.data)
            except ValueError:
                data = {}
            choice_data.update({attr.option.code: data})
        return choices, choice_data

    def _get_unit_price_from_pricelist(self):
        choices, choice_data = self.get_option_choices()
        calc = OptionsCalculator(self.product)
        prices = calc.calculate_costs(choices, self.items_required, choice_data)
        return prices.get_unit_price_incl_tax(self.items_required, self.basket.owner)

    def get_warning(self):
        if self.stockrecord_source == self.PRODUCT_STOCKRECORD:
            super(Line, self).get_warning()
        if self.stockrecord_source == self.OPTIONS_CALCULATOR:
            if self.items_required is None:
                # In this case there is probably a bug in the code
                # execution should not continue
                raise ItemsRequiredException
            if not self.price_incl_tax:
                return
            try:
                current_price_incl_tax, nr_of_units, items_per_pack = (
                    self._get_unit_price_from_pricelist())
            except PriceNotAvailable:
                msg = u"'%(product)s' is no longer available"
                return _(msg) % {'product': self.product.get_title()}
            else:
                if current_price_incl_tax > self.price_incl_tax:
                    msg = ("The price of '%(product)s' has increased from "
                           "%(old_price)s to %(new_price)s since you added it "
                           "to your basket")
                    return _(msg) % {
                        'product': self.product.get_title(),
                        'old_price': currency(self.price_incl_tax),
                        'new_price': currency(current_price_incl_tax)}
                if current_price_incl_tax < self.price_incl_tax:
                    msg = ("The price of '%(product)s' has decreased from "
                           "%(old_price)s to %(new_price)s since you added it "
                           "to your basket")
                    return _(msg) % {
                        'product': self.product.get_title(),
                        'old_price': currency(self.price_incl_tax),
                        'new_price': currency(current_price_incl_tax)}

    def _get_stockrecord_property(self, property):
        if self.stockrecord_source == self.PRODUCT_STOCKRECORD:
            return super(Line, self)._get_stockrecord_property(property)
        if self.stockrecord_source == self.OPTIONS_CALCULATOR:
            
            if self.items_required is None:
                # In this case there is probably a bug in the code
                # execution should not continue
                raise ItemsRequiredException
            try:
                unit_price, nr_of_units, items_per_pack = (
                    self._get_unit_price_from_pricelist())
            except PriceNotAvailable:
                return Decimal('0.00')
            return self._get_stockrecord_choices_property(property, unit_price)

    def get_memory_stockrecord(self, price_excl_tax):
        sr = getattr(self, 'memory_stockrecord', None)
        if sr is None:
            sr = StockRecordForChoices(price_excl_tax)
            setattr(self, 'memory_stockrecord', sr)
        else:
            sr.price_excl_tax = price_excl_tax
        return sr


    def _get_stockrecord_choices_property(self, property, price_excl_tax):
        stockrecord = self.get_memory_stockrecord(price_excl_tax)
        attr = getattr(stockrecord, property, None)
        if attr is None:
            return price_excl_tax
        return attr


class LineAttribute(AbstractLineAttribute):
    # Extra data for option value, for example for custom size
    # it may be {'width': x, 'height': y} dict
    data = models.CharField('Extra choice data', max_length=255, default='',
                            blank=True)
    value_code = models.CharField('Code', max_length=30, default='', blank=True)


class LineAttachment(models.Model):
    line = models.ForeignKey('basket.Line', related_name='attachments',
                             verbose_name=u'Line')
    artwork_item = models.ForeignKey(ArtworkItem, related_name='lines',
                                     verbose_name=u'Artwork item')

    class Meta:
        unique_together = ('line', 'artwork_item')


class Basket(AbstractBasket):
    def add_dynamic_product(self, product, quantity=1, choices=None,
                            attachments=None, choice_data=None):

        if choices is None:
            choices = []

        if choice_data is None:
            choice_data = {}

        if not self.id:
            self.save()

        options = []

        for choice in choices:
            try:
                # choice_data example: {'size':{'width':1, 'height':1}}
                data = choice_data[choice.option.code]
            except KeyError:
                data = {}

            if (choice.option.code == utils.custom_size_option_name() and
                    choice.code == utils.custom_size_option_value()):

                value_data = ','.join(
                    '{0}: {1}'.format(k, v) for k, v in data.iteritems())
                value = '{0} ({1})'.format(choice.caption, value_data)
            else:
                value = choice.caption

            options.append({'option': choice.option,
                            'value': value,
                            'value_code': choice.code,
                            'data': data})

        price_excl_tax = None

        calc = OptionsCalculator(product)

        prices = calc.calculate_costs(choices, quantity, choice_data)

        # line_ref = self._create_line_reference(product, options)
        # if prices.discrete_pricing:
        #     # Put in unique lines, because quantity cannot add up
        #     # with discrete pricing
        #     line_ref = '_'.join([str(quantity), line_ref])

        # Each addition gets it's own line because:
        #   1. discrete priced quantities do no add up
        #   2. even if option choices are exactly the same - it may be different
        #      order with different artwork
        line_ref = uuid.uuid1().hex

        try:
            price_incl_tax, nr_of_units, items_per_pack = (
                prices.get_unit_price_incl_tax(quantity, self.owner))
        except PriceNotAvailable:
            price_incl_tax = None
            nr_of_units = quantity

        line, created = self.lines.get_or_create(
            line_reference=line_ref,
            product=product,
            defaults={
                      'quantity': nr_of_units,
                      'items_required': quantity,
                      'price_excl_tax': price_excl_tax,
                      'price_incl_tax': price_incl_tax,
                      'stockrecord_source': Line.OPTIONS_CALCULATOR})
        if created:
            # Do not use get_or_create here - it is not thread safe, and may cause
            # problems. Just ensure needed option exist before going production.
            o = Option.objects.get(code=settings.OPTION_ITEMSPERPACK)
            line.attributes.create(option=o,
                                   value=items_per_pack,
                                   value_code=items_per_pack,
                                   data='')

            for option_dict in options:
                line.attributes.create(option=option_dict['option'],
                                       value=option_dict['value'],
                                       value_code=option_dict['value_code'],
                                       data=json.dumps(option_dict['data']))
        else:
            line.quantity += nr_of_units
            line.items_required += quantity
            line.save()

        for attachment in attachments:
            line.attachments.create(artwork_item=attachment)

        self.reset_offer_applications()

    add_dynamic_product.alters_data = True

    @property
    def default_wrapper(self):
        wr = getattr(self, "_default_wrapper", None)
        if wr is None:
            wr = DefaultWrapper(get_tax_percent())
            setattr(self, "_default_wrapper", wr)
        return wr

    @property
    def apply_total_price_incl_tax_and_discounts(self):
        return self.default_wrapper.get_total_price_incl_tax(self.total_excl_tax)

    @property
    def apply_total_tax(self):
        return self.default_wrapper.get_tax(self.total_excl_tax)

    def _get_total(self, property):
        # to calculate tax apply tax func to total price, and not sum of
        # all_lines, because tax is given in percent, and prices are shown
        # with only two decimal places, total tax != sum of all_lines tax
        if 'line_price_incl_tax_and_discounts' == property:
            return getattr(self, 'apply_total_price_incl_tax_and_discounts')
        elif 'line_tax' == property:
            return getattr(self, 'apply_total_tax')
        else:
            return super(Basket, self)._get_total(property)

from oscar.apps.basket.models import *
