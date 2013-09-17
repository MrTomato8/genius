from apps.pricelist.models import Price
from apps.options.models import OptionChoice
from django.db import models
import csv
from decimal import Decimal, DecimalException
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.conf import settings
from zlib import crc32
from django.core.exceptions import ObjectDoesNotExist

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')
Partner = models.get_model('partner', 'Partner')
StockRecord = models.get_model('partner', 'StockRecord')

class ImportReport:
    def __init__(self):
        self._skipped = []
        self._imported_total = 0

    def skip(self, column, reason, data):
        self._skipped.append((column, reason, data))

    def success(self):
        self._imported_total += 1

    @property
    def skipped(self):
        for column, reason, data in self._skipped:
            yield column, reason, str(data)

    @property
    def skipped_total(self):
        return len(self._skipped)

    @property
    def imported_total(self):
        return self._imported_total


class OptionError(Exception):
    pass


def import_csv(csvfile, create_options=True, create_choices=True, chirurgical=False):
    '''
    Imports whole pricelist from CSV file.

    Missing option objects are created automatically (staff can edit
    caption and thumbnail later).

    On any error currently processed price record is skipped.

    Empty string fields are excluded from price record.

    Most fields support multiple values(separated by comma without surrounding
    spaces, for example orienataion column may be set to 'portrait,landscape'.
    In this case import will create two price records with different orientations
    and identical other options.
    '''

    report = ImportReport()
    for row in csv.DictReader(csvfile.read().splitlines()):
            rows.append(row)
    qs = Price.objects.filter(state=Price.CURRENT)
    if chirurgical:
        p_list = []
        rows=[]
        
            
        for row in rows:
            try:
                product = Product.objects.get(title=row.pop('product', None))
            except Product.DoesNotExist:
                continue
            p_list.append(product)
        qs.filter(product__in=p_list)
        
    
    qs.update(state=Price.OLD)

    data = {}

    
    for row in rows:
        original_row = row.copy()

        try:
            product = Product.objects.get(title=row.pop('product', None))
        except Product.DoesNotExist:
            report.skip('product', 'not found', original_row)
            continue

        data['product'] = product

        try:
            data['tpl_price'] = Decimal(row.pop('tpl_price', None))
        except DecimalException:
            report.skip('tpl_price', 'bad value', original_row)
            continue

        try:
            data['rpl_price'] = Decimal(row.pop('rpl_price', None))
        except DecimalException:
            report.skip('rpl_price', 'bad value', original_row)
            continue

        try:
            data['min_tpl_price'] = Decimal(row.pop('min_tpl_price', 0))
        except DecimalException:
            data['min_tpl_price'] = Decimal(0)

        try:
            data['min_rpl_price'] = Decimal(row.pop('min_rpl_price', 0))
        except DecimalException:
            data['min_rpl_price'] = Decimal(0)


        try:
            data['quantity'] = Decimal(row.pop('quantity', None))
        except DecimalException:
            report.skip('quantity', 'bad value', original_row)
            continue

        try:
            data['min_area'] = Decimal(row.pop('min_area', None))
        except DecimalException:
            data['min_area'] = Decimal(0)

        try:
            data['items_per_pack'] = int(row.pop('items_per_pack', 1))
        except ValueError:
            data['items_per_pack'] = 1

        try:
            data['min_order'] = Decimal(row.pop('min_order', None))
        except DecimalException:
            report.skip('min_order', 'bad value', original_row)
            continue

        choices = []

        try:
            for col, vals in row.items():
                for val in filter(len, vals.replace(' ', '').split(',')):
                    if create_options:
                        try:
                            o, new = Option.objects.get_or_create(
                                code=slugify(col), type=Option.OPTIONAL)
                        except IntegrityError:
                            report.skip(col, 'integrity error', original_row)
                            raise OptionError
                        if len(o.name) == 0:
                            o.name = o.code
                            o.save()
                    else:
                        try:
                            o = Option.objects.get(code=slugify(col))
                        except Option.DoesNotExist:
                            report.skip(
                                col, 'option missing'.format([val]),
                                original_row)
                            raise OptionError

                    if create_choices:
                        try:
                            c, new = OptionChoice.objects.get_or_create(
                                option=o, code=slugify(val))
                        except IntegrityError:
                            report.skip(col, 'integrity error', original_row)
                            raise OptionError
                    else:
                        try:
                            c = OptionChoice.objects.get(option=o,
                                                         code=slugify(val))
                        except OptionChoice.DoesNotExist:
                            report.skip(
                                col, '{0} choice missing'.format([val]),
                                original_row)
                            raise OptionError

                    choices.append(c)
        except OptionError:
            continue
        
        try:
            product.stockrecord
        except ObjectDoesNotExist:
            partner = Partner.objects.all()[0]
            sku = crc32(product.get_title())
            StockRecord.objects.create(
                product = product, partner = partner, partner_sku = sku
                )
            
        p = Price(**data)
        p.save()
        for choice in choices:
            p.option_choices.add(choice)
        p.save()

        report.success()

    Price.objects.filter(state=Price.OLD).delete()

    # Ensure option for storing items required exist
    o, new = Option.objects.get_or_create(
        code=settings.OPTION_ITEMSPERPACK, type=Option.OPTIONAL)
    if len(o.name) == 0:
        o.name = o.code
        o.save()


    return report
