from django.db import models
from django.core.validators import MinValueValidator

Product = models.get_model('catalogue', 'Product')

# Create your models here.

PRICING_CHOICES = (('unit', 'Per-unit'),
                   ('discrete', 'Discrete'),
                   ('linear', 'Linear'))

STATE_CHOICES = (('active', 'Up to date'),
                 ('updating', 'Update in progress'),
                 ('inactive', 'Not in pricelist'))


class BaseOption(models.Model):
    '''
    Base class for product options

    fields:
    thumbnail - picture to show in wizard
    caption - picture caption
    '''
    caption = models.CharField('Caption', max_length=30, blank=True)
    thumbnail = models.ImageField('Thumbnail', upload_to='options', blank=True)

    def __unicode__(self):
        return self.caption


class GenericOption(BaseOption):
    '''
    Base class for generic options

    fields:
    tag - short handle for option, like "landscape" for orientation or
          "outdoor" for location
    '''

    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(GenericOption, self).save(*args, **kwargs)


class Lamination(GenericOption):
    '''Lamination'''
    pass


class Orientation(GenericOption):
    '''Media orientation'''
    pass


class Printed(GenericOption):
    '''Print sides/colours'''
    pass


class Fold(GenericOption):
    '''Fold type'''
    pass


class Finish(GenericOption):
    '''Finish'''
    pass


class Cover(GenericOption):
    '''Cover type'''
    pass


class Binding(GenericOption):
    '''Binding edge'''
    pass


class Options(GenericOption):
    '''Various uncategorized options, like "printed&untrimmed"'''
    pass


class Location(GenericOption):
    '''Location, like "indoor", "outdoor"'''
    pass


class Frame(GenericOption):
    '''Frame type'''
    pass


class Corners(GenericOption):
    '''Corners to round, like "all" or "top-left"'''
    pass


class Pages(BaseOption):
    '''Page count for multi-page products, like booklets'''
    count = models.DecimalField(max_digits=5, decimal_places=0)

    def save(self, *args, **kwargs):

        if len(self.caption) == 0:
            self.caption = str(self.count)

        super(Pages, self).save(*args, **kwargs)

    def __unicode__(self):
        return ' '.join([str(self.count), 'pages'])

    @staticmethod
    def get_or_create_multiple(counts):
        result = []
        for count in counts:
            # Page count of 0 means no option
            if count > 0:
                obj, n = Pages.objects.get_or_create(count=count)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Weight(BaseOption):
    '''Media weight'''
    value = models.DecimalField('Paper Weight', max_digits=3, decimal_places=0,
                                unique=True)

    def save(self, *args, **kwargs):

        if len(self.caption) == 0:
            self.caption = ''.join([str(self.value), 'gsm'])

        super(Weight, self).save(*args, **kwargs)


class Size(BaseOption):
    '''Media size'''
    width = models.DecimalField('Width', max_digits=10, decimal_places=0)
    height = models.DecimalField('Height', max_digits=10, decimal_places=0)

    def save(self, *args, **kwargs):

        # Always save size in portrait orientation (width < height)
        if self.width > self.height:
            self.width, self.height = self.height, self.width

        if len(self.caption) == 0:
            if self.width == self.height:
                self.caption = ' '.join([str(self.width), 'sq'])
            else:
                self.caption = 'x'.join([str(self.width), str(self.height)])

        super(Size, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('width', 'height')


class Stock(GenericOption):
    '''Stock type'''
    no_weight = models.ManyToManyField(Weight, null=True, blank=True,
                                       help_text='conflicting weight options',
                                       verbose_name=u'weight constraints')
    no_lamination = models.ManyToManyField(Lamination, null=True, blank=True,
                                           help_text='conflicting lamination options',
                                           verbose_name=u'lamination constraints')
    no_finish = models.ManyToManyField(Finish, null=True, blank=True,
                                       help_text='conflicting weight options',
                                       verbose_name=u'finishing contraints')
    no_location = models.ManyToManyField(Location, null=True, blank=True,
                                         help_text='conflicting location options',
                                         verbose_name=u'location constraints')
    no_fold = models.ManyToManyField(Fold, null=True, blank=True,
                                     help_text='conflicting fold options',
                                     verbose_name=u'fold constraints')
    no_printed = models.ManyToManyField(Printed, null=True, blank=True,
                                        help_text='conflicting print options',
                                        verbose_name=u'print constraints')


class Price(models.Model):
    '''
    This model represents pricelist entry for specific set of options for
    given product
    '''

    product = models.ForeignKey(Product)

    state = models.CharField(max_length=10, choices=STATE_CHOICES)
    pricing = models.CharField(max_length=10, choices=PRICING_CHOICES,
                               default='unit')
    tpl_price = models.DecimalField(max_digits=10, decimal_places=3,
                                    validators=[MinValueValidator(0)])
    rpl_price = models.DecimalField(max_digits=10, decimal_places=3,
                                    validators=[MinValueValidator(0)])
    quantity = models.DecimalField(max_digits=10, decimal_places=0,
                                   validators=[MinValueValidator(0)])

    lamination = models.ForeignKey(Lamination, null=True, blank=True)
    orientation = models.ForeignKey(Orientation, null=True, blank=True)
    printed = models.ForeignKey(Printed, null=True, blank=True)
    fold = models.ForeignKey(Fold, null=True, blank=True)
    finish = models.ForeignKey(Finish, null=True, blank=True)
    cover = models.ForeignKey(Cover, null=True, blank=True)
    binding = models.ForeignKey(Binding, null=True, blank=True)
    options = models.ForeignKey(Options, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)
    frame = models.ForeignKey(Frame, null=True, blank=True)
    corners = models.ForeignKey(Corners, null=True, blank=True)
    pages = models.ForeignKey(Pages, null=True, blank=True)
    weight = models.ForeignKey(Weight, null=True, blank=True)
    size = models.ForeignKey(Size, null=True, blank=True)
    stock = models.ForeignKey(Stock, null=True, blank=True)

    def __unicode__(self):
        caption = '{0}({1}) for {2} units of {3} ({4})'

        if self.pricing == 'unit' or self.pricing == 'discrete':
            units = 'units'
        elif self.pricing == 'linear':
            units = 'metres'

        opts = filter(None, [self.lamination, self.orientation, self.printed,
                             self.fold, self.finish, self.cover, self.binding,
                             self.options, self.location, self.frame,
                             self.corners, self.pages, self.weight, self.size,
                             self.stock])

        caption = '{0}({1}) for {2} {3} of {4} ({5})'.format(self.rpl_price,
                                                             self.tpl_price,
                                                             self.quantity,
                                                             units,
                                                             self.product,
                                                             ','.join(map(str, opts)))
        return caption



