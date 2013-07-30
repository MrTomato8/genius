from django.db import models
from django.core.validators import MinValueValidator
from apps.options.models import OptionChoice

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')


class Price(models.Model):
    '''
    This model represents pricelist entry for specific sets of options for
    given product
    '''

    CURRENT, OLD = ('current', 'old')
    STATE_CHOICES = ((CURRENT, 'Current'),
                     (OLD, 'Old'))

    product = models.ForeignKey(Product, related_name='prices')

    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default=CURRENT, editable=False, db_index=True)

    tpl_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        verbose_name='TPL Price')

    rpl_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        verbose_name='RPL Price')

    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], db_index=True)

    min_order = models.IntegerField(
        validators=[MinValueValidator(0)], db_index=True)

    min_area = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
        verbose_name='Minimal Area in square meters (for custom sizes)',
        default=0)

    option_choices = models.ManyToManyField(
        OptionChoice, related_name='prices', blank=True,
        verbose_name=u'Option Choices')

    def __unicode__(self):
        s = '{0}({1}) for {2} units of {3} ({4}). '\
            'Minimum order of {5} units required.'

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
