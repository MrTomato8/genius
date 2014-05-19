from django.db import models
from django.core.validators import MinValueValidator
from apps.options.models import OptionChoice
import re
from decimal import Decimal
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

    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], db_index=True)

    min_order = models.IntegerField(
        validators=[MinValueValidator(0)], db_index=True)

    min_area = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        verbose_name='Minimal Area in square meters (for custom sizes)',
        default=0)

    items_per_pack = models.IntegerField(
        validators=[MinValueValidator(1)], default=1,
        verbose_name=u'Items per pack/sheet')

    option_choices = models.ManyToManyField(
        OptionChoice, related_name='prices', blank=True,
        verbose_name=u'Option Choices')

    def __unicode__(self):
        s = '{0}({1}) for {2} items of {3} ({4}). '\
            'Minimum order of {5} items required.'

        choices = []
        for choice in self.option_choices.all():
            choices.append(str(choice))

        return s.format(
            str(self.rpl_price),
            str(self.tpl_price),
            str(self.quantity),
            str(self.product),
            ','.join(choices),
            str(self.min_order))

    @property
    def options(self):
        return self.option_choices.all()

    class Meta:
        ordering = ['product', 'quantity']


    
