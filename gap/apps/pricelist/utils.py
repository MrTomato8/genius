from apps.pricelist.models import *
import csv
from decimal import Decimal, DecimalException

Product = models.get_model('catalogue', 'Product')


def add_price(*args, **kwargs):

    '''
    This function expands all options passed as list into multi-dimensional
    price matrix. Recursion rocks :)
    '''

    for opt in ['lamination', 'orientation', 'printed', 'fold', 'finish',
                'cover', 'binding', 'options', 'location', 'frame', 'corners',
                'pages', 'weight', 'size', 'stock']:

        if isinstance(kwargs.get(opt, None), list):

            for i in kwargs[opt]:
                kwargs[opt] = i
                add_price(*args, **kwargs)

            break

    else:
        # FIXME: INSERT_OR_UPDATE here
        # uniqueness, no dupes
        p = Price(**kwargs)
        p.save()






class Pricelist:


    @staticmethod
    def importcsv(csvfile):
        data = {}

        for row in csv.DictReader(csvfile):

# TODO: Importing history table with to check in dashboard import results

            # On any error current price record is skipped

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
                # log
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

            #FIXME: move following functonality to Weight object, like in pages
            data['weight'] = []
            for weight in row['weight'].split(','):
                try:
                    value = int(weight)
                except ValueError:
                    value = 0
                    # log here ?
                    continue
                if value > 0:
                    obj, new = Weight.objects.get_or_create(value=value)
                    data['weight'].append(obj)

            if len(data['weight']) == 0:
                data['weight'].append(None)

            add_price(**data)


    def price():
        pass
