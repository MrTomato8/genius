from apps.pricelist.models import *
import csv
from decimal import Decimal, DecimalException
from django.db import IntegrityError

Product = models.get_model('catalogue', 'Product')


def add_price(*args, **kwargs):

    '''
    This function expands all options passed as list into multi-dimensional
    price matrix. Recursion rocks :)
    '''

    for opt in ALL_PRODUCT_OPTIONS:

        if isinstance(kwargs.get(opt, None), list):

            for i in kwargs[opt]:
                kwargs[opt] = i
                add_price(*args, **kwargs)

            break

    else:

        defaults = {}
        for i in ['pricing', 'tpl_price', 'rpl_price']:
            if i in kwargs:
                defaults[i] = kwargs.pop(i)
        # Set updated flag for touched entries
        defaults['state'] = 'active'

        try:
            p, new = Price.objects.get_or_create(defaults=defaults, **kwargs)
        except IntegrityError:
            # log here
            pass
        else:
            if not new:
                for i in defaults:
                    setattr(p, i, defaults[i])

                p.save()


def pick_price():
    pass

# TODO: Implement UNDO (or save/load) functionality
def import_csv(csvfile):
    '''
    Imports whole pricelist from CSV file.

    Missing option objects are created automatically (staff can edit
    caption and thumbnail later).

    On any error currently processed price record is skipped.

    Integer fields that have 0 value are excluded from price record.
    Empty string fields are also excluded from price record.

    Most fields support multiple values(separated by comma without surrounding
    spaces, for example orienataion column may be set to 'portrait,landscape'.
    In this case import will create two price records with different orientations
    and identical other options.
    '''

    Price.objects.filter(state='active').update(state='updating')

    data = {}

    for row in csv.DictReader(csvfile):

        try:
            product = Product.objects.get(title=row['product'])
        except Product.DoesNotExist:
            # log here
            continue

        data['product'] = product

        data['pricing'] = row['pricing']

        try:
            data['tpl_price'] = Decimal(row['tpl_price'])
        except DecimalException:
            # log something like "skipped entry $row"
            continue

        try:
            data['rpl_price'] = Decimal(row['rpl_price'])
        except DecimalException:
            # log
            continue

        try:
            data['quantity'] = int(row['quantity'])
        except ValueError:
            # log
            continue

        data['lamination'] = Lamination.get_or_create_multiple(
            row.get('lamination', '').split(','))
        data['orientation'] = Orientation.get_or_create_multiple(
            row.get('orientation', '').split(','))
        data['printed'] = Printed.get_or_create_multiple(
            row.get('printed', '').split(','))
        data['fold'] = Fold.get_or_create_multiple(
            row.get('fold', '').split(','))
        data['finish'] = Finish.get_or_create_multiple(
            row.get('finish', '').split(','))
        data['cover'] = Cover.get_or_create_multiple(
            row.get('cover', '').split(','))
        data['binding'] = Binding.get_or_create_multiple(
            row.get('binding', '').split(','))
        data['options'] = Options.get_or_create_multiple(
            row.get('options', '').split(','))
        data['location'] = Location.get_or_create_multiple(
            row.get('location', '').split(','))
        data['frame'] = Frame.get_or_create_multiple(
            row.get('frame', '').split(','))
        data['corners'] = Corners.get_or_create_multiple(
            row.get('corners', '').split(','))
        data['stock'] = Stock.get_or_create_multiple(
            row.get('stock', '').split(','))

        try:
            pages = map(int, row['pages'].split(','))
        except ValueError:
            # log here
            continue

        data['pages'] = Pages.get_or_create_multiple(pages)

        try:
            width = int(row['width'])
        except ValueError:
            # log
            continue

        try:
            height = int(row['height'])
        except ValueError:
            # log
            continue

        # All sizes in DB are landscape-oriented
        if width > height:
            width, height = height, width

        data['size'], new = Size.objects.get_or_create(width=width,
                                                       height=height)

        try:
            weight = map(int, row['weight'].split(','))
        except ValueError:
            # log here
            continue

        data['weight'] = Weight.get_or_create_multiple(weight)

        add_price(**data)

    Price.objects.filter(state='updating').update(state='inactive')
