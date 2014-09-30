from django.db import models

from oscar.apps.basket.abstract_models import (
    AbstractBasket, AbstractLine, AbstractLineAttribute)

from apps.options.models import OptionChoice, ArtworkItem
from apps.options.calc import OptionsCalculator, PriceNotAvailable
import simplejson as json
from decimal import Decimal
from oscar.templatetags.currency_filters import currency
from django.utils.translation import ugettext as _
from apps.options import utils
from django.conf import settings
from apps.globals.models import get_tax_percent
from apps.partner.wrappers import DefaultWrapper
import uuid
from django.conf import settings
from apps.basket.exceptions import ItemsRequiredException
from .managers import LineManager


Option = models.get_model('catalogue', 'Option')

class Line(AbstractLine):
    objects = LineManager()

    #width and height for custom size, in mm
    width=models.PositiveIntegerField(default=0)
    height=models.PositiveIntegerField(default=0)

    #choices store all the data in price
    choices = models.ManyToManyField(OptionChoice, related_name='lines+')

    #By Vlad usefull to do something with quotebuilder
    is_dead = models.BooleanField(blank=True, default=False)

    calculator_data = {}
    calculator = None

    @property
    def number_of_files(self):
        return self.attachments.all().count()

    def save(self,*args,**kwargs):
        super(Line,self).save(*args,**kwargs)

    def get_option_choices(self):
        return self.choices.all()

    def get_data(self):
        if self.calculator_data: return self.calculator_data
        data = {}
        data['width']=self.width
        data['height']=self.height
        data['quantity']=self.quantity
        data['number_of_files']=self.number_of_files
        self.calculator_data=data
        return data

    def get_calculator(self):
        if self.calculator: return self.calculator
        calculator=OptionsCalculator(
            self.product,
            self.get_option_choices(),
            self.get_data())
        self.calculator= calculator
        return calculator

    def _get_unit_price_from_pricelist(self):
       return self.unit_price_excl_tax()

    def get_warning(self):
        return

    def product_and_options_description(self):
        attributes = self.choices.all()
        values = [attribute.code for attribute in attributes]
        return ', '.join([self.product.short_title or self.product.title] + values)

    def get_taxes(self):
        return settings.TAX
    _unit_price_excl_tax=None

    @property
    def unit_price_excl_tax(self):
        if self._unit_price_excl_tax: return self._unit_price_excl_tax

        calculator = self.get_calculator()
        price = calculator.price_per_unit(self.basket.owner)
        discount = calculator.get_discount()
        #self.discount(discount,self.quantity)
        #self.consume(self.quantity)
        self._unit_price_excl_tax=price
        return price


    def get_muliline_price_excl_tax(self):
        calc=self.get_calculator()
        return calc.multifile_price()

    def get_muliline_price_tax(self):
        return self.get_muliline_price_excl_tax()*self.get_taxes()

    def get_muliline_price_incl_tax(self):
        return self.get_muliline_price_excl_tax()+self.get_muliline_price_tax()

    @property
    def line_tax(self):
        """Return line tax"""
        return self.quantity * self.unit_tax + self.get_muliline_price_tax()

    @property
    def unit_tax(self):
        """Return tax of a unit"""
        if not self._charge_tax:
            return Decimal('0.00')
        return self.unit_price_excl_tax*self.get_taxes()

    @property
    def unit_price_incl_tax(self):
         return self.unit_price_excl_tax+self.unit_tax



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
    def add_product(
            self, product, quantity=1, choices=None,
        width=0, height=0, attachments = None):

        if attachments is None: attachments= []
        if choices is None:options = []

        # Line reference is used to distinguish between variations of the same
        # product (eg T-shirts with different personalisations)
        line_ref = self._create_line_reference(product, choices)

        # Determine price to store (if one exists).  It is only stored for
        # audit and sometimes caching.
        price_excl_tax, price_incl_tax = None, None



        line, created = self.lines.get_or_create(
            line_reference=line_ref,
            product=product,
            defaults={
                'quantity': quantity,
                'price_excl_tax': price_excl_tax,
                'price_incl_tax': price_incl_tax})
        for option in choices:
                line.choices.add(option)

        if not created:
            line.quantity += quantity
            line.save()

        line.price_excl_tax = line.unit_price_excl_tax
        line.price_incl_tax = line.unit_price_incl_tax
        line.save()
        self.reset_offer_applications()


    def all_lines(self):
        return super(Basket, self).all_lines().exclude(is_dead=True)

    def all_lines_with_dead(self):
        return super(Basket, self).all_lines()

    def dead_lines(self):
        return super(Basket, self).all_lines().filter(is_dead=True)

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
