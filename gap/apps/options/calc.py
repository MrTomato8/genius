from django.db.models import Max
from apps.options import utils
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist

TWOPLACES = Decimal(10) ** -2


class OptionsCalculatorError(Exception):
    pass


class DuplicateQuantities(OptionsCalculatorError):
    pass


class NotEnoughArguments(OptionsCalculatorError):
    pass


class PriceNotAvailable(Exception):
    pass


class CalculatedPrices:
    def __init__(self):
        self._prices = {}
        self.discrete_pricing = False

    def __len__(self):
        return len(self._prices)

    def add(self, quantity, price_data):
        self._prices[quantity] = price_data

    def iteritems(self):
        return self._prices.iteritems()

    def _get_price_attribute(self, quantity, user, attribute):

        if utils.trade_user(user):
            prefix = 'tpl_'
        else:
            prefix = 'rpl_'

        try:
            return self._prices[quantity][prefix + attribute]
        except KeyError:
            raise PriceNotAvailable

    def get_unit_price_incl_tax(self, quantity, user):
        return self._get_price_attribute(quantity, user, 'unit_price_incl_tax')

    def get_price_incl_tax(self, quantity, user):
        return self._get_price_attribute(quantity, user, 'price_incl_tax')


class BaseOptionsCalculator:

    def __init__(self, product):
        self.product = product

    def pick_prices(self, choices, quantity=None):
        '''
        Picks Price objects which statisfy given quantity
        and choice selections
        '''
        prices = self.product.prices.all()
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

    def _apply_choice_data(self, price, choices, choice_data):
        if utils.custom_size_chosen(choices):
            try:
                cargs = choice_data[utils.custom_size_option_name()]
            except KeyError:
                raise NotEnoughArguments(
                    'choice_data argument does not contain {0} key'.format(
                        utils.custom_size_option_name()))

            if 'width' in cargs and 'height' in cargs:
                # calculate area in square metres
                area = Decimal(cargs['width'] * cargs['height']) / Decimal(1000000)

                return price * area

            else:
                raise NotEnoughArguments('For custom size width and height'
                                         'should be supplied')

        # More transformations may be added here in the future
        return price

    def _total(self, price, quantity):
        return (price * quantity).quantize(TWOPLACES, ROUND_HALF_UP)

    def _unit(self, price, quantity):
        return (price / quantity).quantize(TWOPLACES, ROUND_HALF_UP)

    def calculate_costs(self, choices, quantity=None, choice_data=None):
        '''
        Returns CalculatedPrices object

        If custom size option is chosen - then take width and
        height arguments into account. Width and height units are millimeters
        and price value is per square metre for this case.
        '''
        # Totals (price*quantity) are recalculated to make price
        # consistent with basket's price calculation. Basket stores only
        # unit prices with 2 decimal places, so on the calculation one cent may be
        # lost. Here we just need to adapt to Oscar's way of calculating things.
        result = CalculatedPrices()

        if choice_data is None:
            choice_data = {}

        prices = self.pick_prices(choices, quantity)

        # Discrete pricing scheme
        if len(prices) > 1:
            result.discrete_pricing = True

            for price in prices:

                rpl_price = self._apply_choice_data(
                    price.rpl_price, choices, choice_data)
                tpl_price = self._apply_choice_data(
                    price.tpl_price, choices, choice_data)

                rpl_unit_price = self._unit(rpl_price, price.quantity)
                tpl_unit_price = self._unit(tpl_price, price.quantity)

                price_data = {}

                price_data['rpl_price_incl_tax'] = self._total(
                    rpl_unit_price, price.quantity)
                price_data['tpl_price_incl_tax'] = self._total(
                    tpl_unit_price, price.quantity)

                # These are already quantized
                price_data['rpl_unit_price_incl_tax'] = rpl_unit_price
                price_data['tpl_unit_price_incl_tax'] = tpl_unit_price

                result.add(price.quantity, price_data)
        else:
            result.discrete_pricing = False
            try:
                price = prices.get()
            except ObjectDoesNotExist:
                return result

            if quantity is not None:
                rpl_price = self._apply_choice_data(
                    price.rpl_price, choices, choice_data)
                tpl_price = self._apply_choice_data(
                    price.tpl_price, choices, choice_data)

                rpl_unit_price = self._unit(rpl_price, price.quantity)
                tpl_unit_price = self._unit(tpl_price, price.quantity)

                price_data = {}

                price_data['rpl_price_incl_tax'] = self._total(
                    rpl_unit_price, quantity)
                price_data['tpl_price_incl_tax'] = self._total(
                    tpl_unit_price, quantity)

                # These are already quantized
                price_data['rpl_unit_price_incl_tax'] = rpl_unit_price
                price_data['tpl_unit_price_incl_tax'] = tpl_unit_price

                result.add(quantity, price_data)

        return result


class OptionsCalculator(BaseOptionsCalculator):
    pass
