from apps.pricelist.models import Price
from django.db.models import Max
from apps.options.utils import custom_size_chosen
from decimal import Decimal
from django.conf import settings


class OptionsCalculatorError(Exception):
    pass


class DuplicateQuantities(OptionsCalculatorError):
    pass


class NotEnoughArguments(OptionsCalculatorError):
    pass


class BaseOptionsCalculator:

    def __init__(self, product):
        self.product = product

    def pick_prices(self, choices, quantity=None):
        '''
        Picks Price objects which statisfy given quantity
        and choice selections
        '''
        prices = Price.objects.filter(product=self.product)
        if quantity is not None:
            prices = prices.filter(min_order__lte=quantity)

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

        # Abort if duplicate quantities found in discrete priced product.
        # You have to look for invalid lines in pricelist
        if (prices.values('quantity').count() >
                prices.values('quantity').distinct().count()):
            raise DuplicateQuantities

        # Return prices for all found discrete quantities
        return prices

    def calculate_cost(self, choices, quantity=None, choice_data=None):
        '''
        Returns dictionary of available quantities
        each containing dictionaries with following keys:

        'rpl_price_incl_tax': Retail price with tax included
        'rpl_unit_price_incl_tax': Retail unit price with tax included
        'tpl_price_incl_tax': Trade price with tax included
        'tpl_unit_price_incl_tax': Trade unit price with tax included

        If custom size option is chosen - then take width and
        height arguments into account. Width and height units are millimeters
        and price value is per square metre for this case.
        '''
        result = {}

        if choice_data is None:
            choice_data = {}

        coption, cchoice = settings.OPTIONCHOICE_CUSTOMSIZE

        TWOPLACES = Decimal(10) ** -2

        prices = self.pick_prices(choices, quantity)

        for price in prices:

            rpl_price = price.rpl_price
            tpl_price = price.tpl_price

            if custom_size_chosen(choices):
                try:
                    cargs = choice_data[coption]
                except KeyError:
                    raise NotEnoughArguments(
                        'choice_data argument does not contain {0} key'.format(coption))

                if 'width' in cargs and 'height' in cargs:
                    # calculate area in square metres
                    area = Decimal(cargs['width'] * cargs['height']) / Decimal(1000000)

                    rpl_price = rpl_price * area
                    tpl_price = tpl_price * area
                else:
                    raise NotEnoughArguments('For custom size width and height'
                                             'should be supplied')

            # In pricelist price may be supplied for multiple
            # units (price.quantity).
            # For price calculation we need unit price.

            rpl_unit_price = rpl_price / price.quantity
            tpl_unit_price = tpl_price / price.quantity

            if quantity is not None:
                result[quantity] = {}

                result[quantity]['rpl_price_incl_tax'] = (
                    rpl_unit_price * quantity).quantize(TWOPLACES)
                result[quantity]['tpl_price_incl_tax'] = (
                    tpl_unit_price * quantity).quantize(TWOPLACES)

                result[quantity]['rpl_unit_price_incl_tax'] = (
                    rpl_unit_price).quantize(TWOPLACES)
                result[quantity]['tpl_unit_price_incl_tax'] = (
                    tpl_unit_price).quantize(TWOPLACES)
            else:
                result[price.quantity] = {}

                result[price.quantity]['rpl_price_incl_tax'] = (
                    rpl_price).quantize(TWOPLACES)
                result[price.quantity]['tpl_price_incl_tax'] = (
                    tpl_price).quantize(TWOPLACES)
                result[price.quantity]['rpl_unit_price_incl_tax'] = (
                    rpl_unit_price).quantize(TWOPLACES)
                result[price.quantity]['tpl_unit_price_incl_tax'] = (
                    tpl_unit_price).quantize(TWOPLACES)

        return result


class OptionsCalculator(BaseOptionsCalculator):
    pass
