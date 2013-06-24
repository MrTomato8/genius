from django.db import models
from django.core.validators import MinValueValidator

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')


class OptionChoice(models.Model):
    code = models.SlugField('Code', max_length=30)

    option = models.ForeignKey(Option, related_name='choices')
    conflicts_with = models.ManyToManyField(
        'self', blank=True, verbose_name=u'Conflicting Choices')

    caption = models.CharField('Caption', max_length=30, blank=True)
    thumbnail = models.ImageField('Thumbnail', upload_to='options', blank=True)

    def __unicode__(self):
        return ''.join([str(self.option), ': ', self.code])

    def save(self, *args, **kwargs):

        if len(self.caption) == 0:
            self.caption = self.code

        super(OptionChoice, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('option', 'code')


class Price(models.Model):
    '''
    This model represents pricelist entry for specific sets of options for
    given product
    '''

    CURRENT, OLD = ('current', 'old')
    STATE_CHOICES = ((CURRENT, 'Current'),
                     (OLD, 'Old'))

    product = models.ForeignKey(Product)

    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default=CURRENT, editable=False, db_index=True)

    tpl_price = models.DecimalField(
        max_digits=10, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='TPL Price')

    rpl_price = models.DecimalField(
        max_digits=10, decimal_places=3, validators=[MinValueValidator(0)],
        verbose_name='RPL Price')

    quantity = models.DecimalField(max_digits=10, decimal_places=3,
                                   validators=[MinValueValidator(0)])
    option_choices = models.ManyToManyField(
        OptionChoice, blank=True, verbose_name=u'Option Choices')

    def __unicode__(self):
        s = '{0}({1}) for {2} units of {3} ({4})'

        choices = []
        for choice in self.option_choices.all():
            choices.append(str(choice))

        return s.format(
            str(self.rpl_price),
            str(self.tpl_price),
            str(self.quantity),
            str(self.product),
            ','.join(choices))

    @property
    def options(self):
        return self.option_choices.all()
