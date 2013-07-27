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

    def get_option_choices(self):
        choice_data = {}
        choices = []
        for attr in self.attributes.all():
            # May be a lot of excetpions here, but it will mean problems in
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
        prices = calc.calculate_costs(choices, self.quantity, choice_data)
        return prices.get_unit_price_incl_tax(self.quantity, self.basket.owner)

    def get_warning(self):
        if self.stockrecord_source == self.PRODUCT_STOCKRECORD:
            super(Line, self).get_warning()
        if self.stockrecord_source == self.OPTIONS_CALCULATOR:
            if not self.price_incl_tax:
                return
            try:
                current_price_incl_tax = self._get_unit_price_from_pricelist()
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
            try:
                return self._get_unit_price_from_pricelist()
            except PriceNotAvailable:
                return Decimal('0.00')


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

        line_ref = self._create_line_reference(product, options)

        price_excl_tax = None

        calc = OptionsCalculator(product)
        prices = calc.calculate_costs(choices, quantity, choice_data)
        try:
            price_incl_tax = prices.get_unit_price_incl_tax(quantity, self.owner)
        except PriceNotAvailable:
            price_incl_tax = None

        line, created = self.lines.get_or_create(
            line_reference=line_ref,
            product=product,
            defaults={'quantity': quantity,
                      'price_excl_tax': price_excl_tax,
                      'price_incl_tax': price_incl_tax,
                      'stockrecord_source': Line.OPTIONS_CALCULATOR})
        if created:
            for option_dict in options:
                line.attributes.create(option=option_dict['option'],
                                       value=option_dict['value'],
                                       value_code=option_dict['value_code'],
                                       data=json.dumps(option_dict['data']))
        else:
            line.quantity += quantity
            line.save()

        for attachment in attachments:
            line.attachments.create(artwork_item=attachment)

        self.reset_offer_applications()

    add_dynamic_product.alters_data = True


from oscar.apps.basket.models import *
