from django.db import models
from django.core.validators import MinValueValidator
from apps.options.models import OptionChoice
import re
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from decimal import Decimal
import csv

from .managers import PricelistManager

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')

class CsvRow(models.Model):
    quantity_discount=models.TextField()
    base_tpl_price = models.DecimalField(
        max_digits=11, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='Price for trade customers')

    base_rpl_price = models.DecimalField(
        max_digits=11, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='Price for retail customers')

    def breaker(self, element):
        quantity, anomaly = element.split('-')
        anomaly = re.findall('\d+\.?\d*',anomaly)
        try:
            discount = Decimal(anomaly[0])
        except:
            discount = Decimal(0)
        try:
            fixed = Decimal(anomaly[1])
        except:
            fixed = Decimal(0)
        return quantity,  discount, fixed

    def update_field(self,quantity_discount,*args,**kwargs):
        self.quantity_discount=quantity_discount
        self.save(*args,**kwargs)
        for element in self.quantity_discount.split(','):

            try:
                quantity, discount, fixed = self.breaker(element)
            except:
                pass
            else:
                price = self.prices.get(quantity=quantity)

                price.tpl_price = self.base_tpl_price*(1-Decimal(discount)/100)+fixed
                price.rpl_price = self.base_rpl_price*(1-Decimal(discount)/100)+fixed
                price.save()



class Price(models.Model):
    '''
    This model represents pricelist entry for specific sets of options for
    given product
    '''

    CURRENT, OLD = ('current', 'old')
    STATE_CHOICES = ((CURRENT, 'Current'),
                     (OLD, 'Old'))
    csv =  models.ForeignKey(CsvRow, related_name='prices', null=True, editable=False )
    product = models.ForeignKey(Product, related_name='prices')

    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default=CURRENT, editable=False, db_index=True)

    tpl_price = models.DecimalField(
        max_digits=11, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='Price for trade customers')

    rpl_price = models.DecimalField(
        max_digits=11, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='Price for retail customers')

    min_tpl_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        verbose_name='Minimal price for trade customers', default=0)

    min_rpl_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        verbose_name='Minimal price for retail customers', default=0)

    min_order = models.IntegerField(
        validators=[MinValueValidator(0)], db_index=True)

    min_area = models.DecimalField(
        max_digits=10, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='Minimal length in square meters (for custom sizes) prec=1mm^2',
        default=0)

    min_length = models.DecimalField(
        max_digits=10, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='Minimal length in meters (for custom sizes) prec=1mm',
        default=0)

    media_width = models.DecimalField(
        max_digits=5, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='Width of the print media in meters (for custom sizes) prec=1mm',
        default=0)

    items_per_pack = models.IntegerField(
        validators=[MinValueValidator(1)], default=1,
        verbose_name=u'Items per pack/sheet')

    option_choices = models.ManyToManyField(
        OptionChoice, related_name='prices', blank=True,
        verbose_name=u'Option Choices', db_index= True)

    option_cost = models.DecimalField(
        max_digits=5, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='cost of the option',
        default=0)

    objects=PricelistManager()

    def __unicode__(self):
        s = '{0}({1}) {3} ({4}). '\
            'Minimum order of {5} items required.'

        choices = []
        for choice in self.option_choices.all():
            choices.append(str(choice))

        return s.format(
            str(self.rpl_price),
            str(self.tpl_price),
            '',
            str(self.product),
            ','.join(choices),
            str(self.min_order))

    @property
    def options(self):
        return self.option_choices.all()

class Discount(models.Model):
    quantity=models.DecimalField(max_digits=6, decimal_places=2)
    discount=models.DecimalField(max_digits=4, decimal_places=2)
    price = models.ForeignKey(Price, related_name="discounts",db_index=True)
    class Meta:
        ordering = ['-quantity']

class CSV(models.Model):
    def upload_to(self, filename):
        return settings.MEDIA_ROOT+'/csv/'+filename

    name = models.CharField(max_length=150, db_index=True)
    csv_file= models.FileField(max_length=500, upload_to=upload_to)

    def get_absolute_url(self):
        return reverse_lazy('csvupdate', kwargs={'pk':self.pk})

    def rows(self):
        for row in csv.reader(self.csv_file):
            yield row

