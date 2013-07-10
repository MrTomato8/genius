from apps.pricelist.models import Price
from apps.options.models import OptionChoice
from django.db import models
import csv
from decimal import Decimal, DecimalException
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.db.models import Max


Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')


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


class MatchingPriceNotFound(Exception):
    pass


class DuplicateQuantities(Exception):
    pass


def pick_price(product, quantity, choices):

    # Keep prices for requested product where quantity satisfies min_order
    prices = Price.objects.filter(product=product, min_order__lte=quantity)

    # Keep prices for selected options only
    for choice in choices:
        prices = prices.filter(option_choices=choice)

    # There may be several different prices for the same quantity
    # with different suitable min_order value. For example:
    # unit price $10 for min_order of 5 units
    # unit price $9 for min order of 20 units
    # unit price $8 for min order of 30 units
    #
    # so for the requested quantity=50 closest
    # will be MAX(min_order) = 30
    if prices.count() > 1:
        min_order = prices.aggregate(Max('min_order'))['min_order__max']
        prices = prices.filter(min_order=min_order)

    # I am not sure if this is right place to do sanity checking on pricelist
    # TODO: Rethink this part
    if prices.values('quantity').count() > prices.values('quantity').distinct().count():
        raise DuplicateQuantities

    # At this point only prices with distinct quantities are left in queryset
    # If there is only 1 distinct quantity - then pricing is per-unit
    # Else - pricing is discrete
    if prices.count() == 1:
        return prices.get()
    elif prices.count > 1:
        try:
            return prices.get(quantity=quantity)
        except Price.DoesNotExist:
            raise MatchingPriceNotFound
    else:
        raise MatchingPriceNotFound


def import_csv(csvfile, create_options=True, create_choices=True):
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

    Price.objects.filter(state=Price.CURRENT).update(state=Price.OLD)

    data = {}

    for row in csv.DictReader(csvfile.read().splitlines()):

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
            data['quantity'] = Decimal(row.pop('quantity', None))
        except DecimalException:
            report.skip('quantity', 'bad value', original_row)
            continue

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

        p = Price(**data)
        p.save()
        for choice in choices:
            p.option_choices.add(choice)
        p.save()

        report.success()

    Price.objects.filter(state=Price.OLD).delete()

    return report
