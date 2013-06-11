from django.db import models

Product = models.get_model('catalogue', 'Product')

# Create your models here.

ORIENTATION_CHOICES = (('n/a', 'Not Applicable'),
                       ('portrait', 'Portrait'),
                       ('landscape', 'Landscape'))

SIDES_CHOICES = ((1, 'Single-Sided'), (2, 'Double-Sided'))

PRINTING_CHOICES = (('n/a', 'Not Applicable'),
                    ('1/0', 'B/W single-sided'),
                    ('1/1', 'B/W double-sided'),
                    ('4/0', 'Colour single-sided'),
                    ('4/1', 'One colour side, One B/W side'),
                    ('4/4', 'Colur double-sided'))

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
    caption = models.CharField(max_length=30)
    thumbnail = models.ImageField(upload_to='options')


class Orientation(BaseOption):
    '''Media orientation'''
    orientation = models.CharField(max_length=15, choices=ORIENTATION_CHOICES)


class Size(BaseOption):
    '''Media size'''
    width = models.DecimalField(max_digits=10, decimal_places=0)
    height = models.DecimalField(max_digits=10, decimal_places=0)


class Weight(BaseOption):
    '''Media weight'''
    weight = models.DecimalField(max_digits=3, decimal_places=0)


class Coating(BaseOption):
    '''Lamination type'''
    coating = models.CharField(max_length=30)


class Fold(BaseOption):
    '''Fold type'''
    fold = models.CharField(max_length=30)


class Sides(BaseOption):
    '''Single-sided or double-sided printing'''
    sides = models.DecimalField(max_digits=1, decimal_places=0, choices=SIDES_CHOICES)


class Media(BaseOption):
    '''Media(paper) type'''
    media = models.CharField(max_length=30)


class Printing(BaseOption):
    '''Printing colour'''
    colour = models.CharField(max_length=3, choices=PRINTING_CHOICES)


class Corners(BaseOption):
    '''Number of rounded corners'''
    corners = models.DecimalField(max_digits=1, decimal_places=0)


class Price(models.Model):
    '''
    This model represents pricelist entry for specific set of options for
    given product
    '''

    product = models.ForeignKey(Product)

    pricing = models.CharField(max_length=10, choices=PRICING_CHOICES)
    tpl_price = models.DecimalField(max_digits=10, decimal_places=3)
    rpl_price = models.DecimalField(max_digits=10, decimal_places=3)
    quantity = models.DecimalField(max_digits=10, decimal_places=0)
    pages = models.DecimalField(max_digits=10, decimal_places=0)
    size = models.ForeignKey(Size)
    weight = models.ForeignKey(Weight)
    coating = models.ForeignKey(Coating)
    fold = models.ForeignKey(Fold)
    sides = models.ForeignKey(Sides)
    media = models.ForeignKey(Media)
    printing = models.ForeignKey(Printing)
    corners = models.ForeignKey(Corners)
    state = models.CharField(max_length=10, choices=STATE_CHOICES)
