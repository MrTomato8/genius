from django.db import models
from django.core.validators import MinValueValidator
import hashlib

Product = models.get_model('catalogue', 'Product')

# Create your models here.

PRICING_CHOICES = (('unit', 'Per-unit'),
                   ('discrete', 'Discrete'),
                   ('linear', 'Linear'))

STATE_CHOICES = (('active', 'Up to date'),
                 ('updating', 'Update in progress'),
                 ('inactive', 'Not in pricelist'))

ALL_PRODUCT_OPTIONS = ['lamination', 'orientation', 'printed', 'fold', 'finish',
                       'front_cover', 'back_cover', 'binding', 'options',
                       'location', 'frame', 'corners', 'pages', 'weight',
                       'size', 'stock', 'print_stock']


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


# I've failed to find the simple way to avoid copy-pasting here
# If I create parent class for following objects - setting 'tag' to unique
# Will fail if different option classes have same tag value(For example 'none'
# for lamination and front_cover). It is the way how Django ORM works to blame,
# not me :)
class Lamination(BaseOption):
    '''Lamination'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Lamination, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Orientation(BaseOption):
    '''Media orientation'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Orientation, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Printed(BaseOption):
    '''Print sides/colours'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Printed, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Fold(BaseOption):
    '''Fold type'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Fold, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Finish(BaseOption):
    '''Finish'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Finish, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Cover(BaseOption):
    '''Cover type'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Cover, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Binding(BaseOption):
    '''Binding edge'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Binding, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Options(BaseOption):
    '''Various uncategorized options, like "printed&untrimmed"'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Options, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Location(BaseOption):
    '''Location, like "indoor", "outdoor"'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Location, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Frame(BaseOption):
    '''Frame type'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Frame, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Corners(BaseOption):
    '''Corners to round, like "all" or "top-left"'''
    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Corners, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Pages(BaseOption):
    '''Page count for multi-page products, like booklets'''
    count = models.DecimalField(max_digits=5, decimal_places=0, unique=True)

    @property
    def tag(self):
        return ''.join([str(self.count), 'pages'])

    def save(self, *args, **kwargs):

        if len(self.caption) == 0:
            self.caption = str(self.count)

        super(Pages, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, counts):
        result = []
        for count in counts:
            # Page count of 0 means no option
            if count > 0:
                obj, n = cls.objects.get_or_create(count=count)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Weight(BaseOption):
    '''Media weight'''
    value = models.DecimalField('Paper Weight', max_digits=3, decimal_places=0,
                                unique=True)

    @property
    def tag(self):
        return ''.join([str(self.value), 'gsm'])

    def save(self, *args, **kwargs):

        if len(self.caption) == 0:
            self.caption = ''.join([str(self.value), 'gsm'])

        super(Weight, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, values):
        result = []
        for value in values:
            # Weight of 0 means no option
            if value > 0:
                obj, n = cls.objects.get_or_create(value=value)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Size(BaseOption):
    '''Media size'''
    width = models.DecimalField('Width', max_digits=10, decimal_places=0)
    height = models.DecimalField('Height', max_digits=10, decimal_places=0)

    @property
    def tag(self):
        return 'x'.join([str(self.width), str(self.height)])

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


class Stock(BaseOption):
    '''Stock type'''
    no_weight = models.ManyToManyField(
        Weight, null=True, blank=True, help_text='conflicting weight options',
        verbose_name=u'weight constraints')

    no_lamination = models.ManyToManyField(
        Lamination, null=True, blank=True,
        help_text='conflicting lamination options',
        verbose_name=u'lamination constraints')

    no_finish = models.ManyToManyField(
        Finish, null=True, blank=True, help_text='conflicting weight options',
        verbose_name=u'finishing contraints')

    no_location = models.ManyToManyField(
        Location, null=True, blank=True,
        help_text='conflicting location options',
        verbose_name=u'location constraints')

    no_fold = models.ManyToManyField(
        Fold, null=True, blank=True, help_text='conflicting fold options',
        verbose_name=u'fold constraints')

    no_printed = models.ManyToManyField(
        Printed, null=True, blank=True, help_text='conflicting print options',
        verbose_name=u'print constraints')

    tag = models.CharField(max_length=30, unique=True)

    def save(self, *args, **kwargs):

        # When creating object programmatically copy tag to caption
        # so it is more convenient for the user to edit caption later
        if len(self.caption) == 0:
            self.caption = self.tag

        super(Stock, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_multiple(cls, tags):
        result = []
        for tag in tags:
            # skip empty values
            if len(tag) > 0:
                obj, n = cls.objects.get_or_create(tag=tag)
                result.append(obj)

        if result == []:
            return None
        else:
            return result


class Price(models.Model):
    '''
    This model represents pricelist entry for specific set of options for
    given product
    '''

    product = models.ForeignKey(Product)

    state = models.CharField(max_length=10, choices=STATE_CHOICES,
                             default='active')

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
    front_cover = models.ForeignKey(Cover, related_name='price_front_cover',
                                    null=True, blank=True)
    back_cover = models.ForeignKey(Cover, related_name='rpice_back_cover',
                                   null=True, blank=True)
    binding = models.ForeignKey(Binding, null=True, blank=True)
    options = models.ForeignKey(Options, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)
    frame = models.ForeignKey(Frame, null=True, blank=True)
    corners = models.ForeignKey(Corners, null=True, blank=True)
    pages = models.ForeignKey(Pages, null=True, blank=True)
    weight = models.ForeignKey(Weight, null=True, blank=True)
    size = models.ForeignKey(Size, null=True, blank=True)
    stock = models.ForeignKey(Stock, related_name='price_stock', null=True,
                              blank=True)
    print_stock = models.ForeignKey(Stock, related_name='price_print_stock',
                                    null=True, blank=True)
    hashcol = models.SlugField(unique=True, editable=False)

    @property
    def enabled_options(self):

        '''
        Returns a list of option objects which have been set for this Price
        '''

        attr = lambda x: getattr(self, x, None)
        return filter(None, map(attr, ALL_PRODUCT_OPTIONS))

    def save(self, *args, **kwargs):

        # unique_together doesn't work with MySQL in this case
        # (MySQL has 16 columns per index limit)
        # so we use hashcol method here

        # Without unique index add_price may produce
        # dupes (objects get_or_create is not atomic)

        s = '-'.join([self.product.slug,
                      self.pricing,
                      str(self.quantity)])

        for opt in self.enabled_options:
            s = '-'.join([s, opt.tag])

        self.hashcol = hashlib.sha1(s).hexdigest()
        super(Price, self).save(*args, **kwargs)

    def __unicode__(self):
        caption = '{0}({1}) for {2} units of {3} ({4})'

        if self.pricing == 'unit' or self.pricing == 'discrete':
            units = 'units'
        elif self.pricing == 'linear':
            units = 'metres'

        caption = '{0}({1}) for {2} {3} of {4} ({5})'.format(
            self.rpl_price,
            self.tpl_price,
            self.quantity,
            units,
            self.product,
            ','.join(map(str, self.enabled_options)))
        return caption
