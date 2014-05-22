# -*- coding: utf-8 -*-
from apps.pricelist.models import Price, CsvRow
from apps.options.models import OptionChoice
from django.db import models
import csv
from decimal import Decimal, DecimalException
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.conf import settings
from zlib import crc32
from django.core.exceptions import ObjectDoesNotExist
import re

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


def import_csv(csvfile, create_options=True, create_choices=True, chirurgical=True):
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
    rows=[]
    for row in csv.DictReader(csvfile.read().splitlines()):
        rows.append(row)
    qs = Price.objects.filter(state=Price.CURRENT)
    if chirurgical:
        p_list = []
        for row in rows:
            try:
                product = Product.objects.get(title=row['product'])
            except Product.DoesNotExist:
                continue
            p_list.append(product)
        qs = qs.filter(product__in=p_list)
    
    qs.update(state=Price.OLD)
    data = {}
    option_cache = {}
    coiches_cache= {}
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
        except:
            report.skip('tpl_price', 'bad value', original_row)
            continue

        try:
            data['rpl_price'] = Decimal(row.pop('rpl_price', None))
        except:
            report.skip('rpl_price', 'bad value', original_row)
            continue

        try:
            data['min_tpl_price'] = Decimal(row.pop('min_tpl_price', 0))
        except:
            data['min_tpl_price'] = Decimal(0)

        try:
            data['min_rpl_price'] = Decimal(row.pop('min_rpl_price', 0))
        except:
            data['min_rpl_price'] = Decimal(0)


        try:
            data['quantity'] = Decimal(row.pop('quantity', None))
        except:
            report.skip('quantity', 'bad value', original_row)
            continue
        # quantity-discount
        try:
            raw_quantity_discount = row.pop('quantity-discount', None)
            quantity_discount = raw_quantity_discount.split(',')
        except:
            quantity_discount = False
            pass
            
            
        try:
            data['min_area'] = Decimal(row.pop('min_area', None))
        except:
            data['min_area'] = Decimal(0)

        try:
            data['items_per_pack'] = int(row.pop('items_per_pack', 1))
        except ValueError:
            data['items_per_pack'] = 1

        try:
            data['min_order'] = Decimal(row.pop('min_order', None))
        except:
            report.skip('min_order', 'bad value', original_row)
            continue

        choices = []

        try:
            for col, vals in row.items():
                for val in filter(len, vals.replace(', ', ',').replace(' ,',',').split(',')):
                    slug = slugify(col)
                    try:
                        o=option_cache[slug]
                    except:
                        if create_options:
                            try:
                                o, new = Option.objects.get_or_create(
                                    code=slug, defaults={'type':Option.OPTIONAL})
                            except IntegrityError:
                                report.skip(col, 'integrity error', original_row)
                                raise OptionError
                            if len(o.name) == 0:
                                o.name = o.code
                                o.save()
                                
                        else:
                            try:
                                o = Option.objects.get(code=slug)
                            except Option.DoesNotExist:
                                report.skip(
                                    col, 'option missing'.format([val]),
                                    original_row)
                                raise OptionError
                        #chache option
                        option_cache[slug]=o
                        
                    slug = slugify(val)
                    try:
                        c = coiches_cache[(slug,o)]
                    except:
                        if create_choices:
                            try:
                                c, new = OptionChoice.objects.get_or_create(
                                    option=o, code=slug)
                            except IntegrityError:
                                report.skip(col, 'integrity error', original_row)
                                raise OptionError
                        else:
                            try:
                                c = OptionChoice.objects.get(option=o,
                                                             code=slug)
                            except OptionChoice.DoesNotExist:
                                report.skip(
                                    col, '{0} choice missing'.format([val]),
                                    original_row)
                                raise OptionError
                            coiches_cache[(slug,o)] = c

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
        
        #effettuare un for loop e salvare ricursivamente **data
        #magari creando l'opzione base_price
        if quantity_discount:
            base_tpl_price = data['tpl_price']
            base_rpl_price = data['rpl_price']
            csvrow = CsvRow(
                quantity_discount=','.join(quantity_discount),
                base_tpl_price=base_tpl_price,
                base_rpl_price=base_rpl_price
                )
            csvrow.save()
            for element in quantity_discount:
                try:
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
                    data['quantity'] = int(quantity)
                    data['tpl_price'] = base_tpl_price*(1-discount/100)+fixed
                    data['rpl_price'] = base_rpl_price*(1-discount/100)+fixed
                    
                    p = Price(**data)
                    p.csv=csvrow
                    p.save()
                    for choice in choices:
                        p.option_choices.add(choice)
                    p.save()
                except:
                    pass
        else:
            p = Price(**data)
            p.save()
            for choice in choices:
                p.option_choices.add(choice)
            p.save()
            
        report.success()
    for price in Price.objects.filter(state=Price.OLD):
        try:
            price.csv.delete()
        except:
            pass
    Price.objects.filter(state=Price.OLD).delete()
    # clean up all non-used option choices
    if create_choices:
        OptionChoice.objects.filter(prices = None).delete()
    # Ensure option for storing items required exist
    o, new = Option.objects.get_or_create(
        code=settings.OPTION_ITEMSPERPACK, defaults={'type':Option.OPTIONAL})
    if len(o.name) == 0:
        o.name = o.code
        o.save()
    
    return report
