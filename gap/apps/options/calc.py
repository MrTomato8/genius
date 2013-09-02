from django.db.models import Min, Max
from apps.options import utils
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
from django.core.exceptions import ObjectDoesNotExist
from collections import OrderedDict

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
        self.min_order = 1
        self.min_area = Decimal(0)

    def __len__(self):
        return len(self._prices)

    def add(self, quantity, price_data):
        self._prices[quantity] = price_data

    def iteritems(self):
        return self._prices.iteritems()

    def values(self):
        return self._prices.values()

    def ordered(self):
        return OrderedDict(sorted(self._prices.iteritems(), key=lambda t: t[0]))

    def _get_price_attribute(self, quantity, user, attribute):

        if utils.trade_user(user):
            prefix = 'tpl_'
        else:
            prefix = 'rpl_'

        try:
            return (
                self._prices[quantity][prefix + attribute],
                self._prices[quantity]['nr_of_units'],
                self._prices[quantity]['items_per_pack'])
        except KeyError:
            raise PriceNotAvailable

    def get_unit_price_incl_tax(self, quantity, user):
        return self._get_price_attribute(quantity, user, 'unit_price_incl_tax')

    def get_price_incl_tax(self, quantity, user):
        return self._get_price_attribute(quantity, user, 'price_incl_tax')
    
    def add_price_history(self, tpl_prices, rpl_prices):
        self.vanilla_tpl_prices = tpl_prices
        self.vanilla_rpl_prices = rpl_prices
        pass
    
    def get_min_rpl_price(self):
        return min(self.vanilla_rpl_prices)
    
    def get_min_tpl_price(self):
        return min(self.vanilla_tpl_prices)

class BaseOptionsCalculator:

    def __init__(self, product):
        self.product = product

    def _get_area(self, choice_data):

        result = 0

        try:
            cargs = choice_data[utils.custom_size_option_name()]
        except KeyError:
            raise NotEnoughArguments(
                'choice_data argument does not contain {0} key'.format(
                    utils.custom_size_option_name()))

        if 'width' in cargs and 'height' in cargs:
            # calculate area in square metres
            area = Decimal(cargs['width'] * cargs['height']) / Decimal(1000000)

            result = area

        else:
            raise NotEnoughArguments('For custom size width and height'
                                     'should be supplied')

        return result

    def pick_prices(self, choices, choice_data, quantity=None):
        '''
        Picks Price objects which statisfy given quantity
        and choice selections
        '''
        prices = self.product.prices.all()

        custom_size = utils.custom_size_chosen(choices)

        discrete = prices.values('quantity').distinct().count() > 1

        if quantity is not None:
            prices = prices.filter(min_order__lte=quantity)

        if custom_size:
            area = self._get_area(choice_data)
            prices = prices.filter(min_area__lte=area)

        # Keep prices for selected options only
        for choice in choices:
            prices = prices.filter(option_choices=choice)

        # There may be several minimal areas matched, lets get closest one
        min_area_max = prices.aggregate(Max('min_area'))['min_area__max']
        prices = prices.filter(min_area=min_area_max)

        # There may be several different prices for the same quantity
        # with different suitable min_order value. For example:
        # unit price $10 for min_order of 5 units
        # unit price $9 for min order of 20 units
        # unit price $8 for min order of 30 units
        #
        # so for the requested quantity=50 closest
        # will be MAX(min_order) = 30

        min_order_max = prices.aggregate(Max('min_order'))['min_order__max']
        prices = prices.filter(min_order=min_order_max)

        # Abort if duplicate quantities found in discrete priced product.
        # You have to look for invalid lines in pricelist
        if (prices.values('quantity').count() >
                prices.values('quantity').distinct().count()):
            raise DuplicateQuantities

        # Return prices for all found discrete quantities
        return prices, discrete

    def _apply_choice_data(self, price, choices, choice_data):
        if utils.custom_size_chosen(choices):
            return price * self._get_area(choice_data)

        #elif ... More transformations may be added here in the future
        else:
            return price

    def _calc_units(self, items_per_pack, quantity):
        if items_per_pack == 1:
            return 1
        if items_per_pack == quantity:
            return 1
        return (Decimal(quantity) / Decimal(items_per_pack)).quantize(
            Decimal('1.'), rounding=ROUND_UP)

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

        prices, discrete = self.pick_prices(choices, choice_data, quantity)
        
        # vanilla price history
        rpl_price_history = []
        tpl_price_history = []
        
        # Discrete pricing scheme
        if discrete:
            result.discrete_pricing = True

            for price in prices:
                
                rpl_price_history.append(price.rpl_price)
                tpl_price_history.append(price.tpl_price)

                rpl_price = self._apply_choice_data(
                    price.rpl_price, choices, choice_data)
                tpl_price = self._apply_choice_data(
                    price.tpl_price, choices, choice_data)

                if rpl_price < price.min_rpl_price:
                    rpl_price = price.min_rpl_price

                if tpl_price < price.min_tpl_price:
                    tpl_price = price.min_tpl_price

                items_per_pack = price.items_per_pack
                nr_of_units = self._calc_units(
                    items_per_pack, price.quantity)

                rpl_unit_price = self._unit(rpl_price, nr_of_units)
                tpl_unit_price = self._unit(tpl_price, nr_of_units)

                price_data = {}

                price_data['nr_of_units'] = nr_of_units
                price_data['items_per_pack'] = items_per_pack

                price_data['rpl_price_incl_tax'] = self._total(
                    rpl_unit_price, nr_of_units)
                price_data['tpl_price_incl_tax'] = self._total(
                    tpl_unit_price, nr_of_units)

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
            
            rpl_price_history.append(price.rpl_price)
            tpl_price_history.append(price.tpl_price)
            
            if quantity is not None:
                
                rpl_price = self._apply_choice_data(
                    price.rpl_price, choices, choice_data)
                tpl_price = self._apply_choice_data(
                    price.tpl_price, choices, choice_data)

                items_per_pack = price.items_per_pack
                nr_of_units = self._calc_units(
                    items_per_pack, price.quantity)

                nr_of_units_required = self._calc_units(
                    items_per_pack, quantity)

                rpl_unit_price = self._unit(rpl_price, nr_of_units)
                tpl_unit_price = self._unit(tpl_price, nr_of_units)

                rpl_min_unit_price = self._unit(
                    price.min_rpl_price, nr_of_units_required)

                tpl_min_unit_price = self._unit(
                    price.min_tpl_price, nr_of_units_required)

                if rpl_unit_price < rpl_min_unit_price:
                    rpl_unit_price = rpl_min_unit_price

                if tpl_unit_price < tpl_min_unit_price:
                    tpl_unit_price = tpl_min_unit_price

                price_data = {}

                price_data['nr_of_units'] = nr_of_units_required
                price_data['items_per_pack'] = items_per_pack

                price_data['rpl_price_incl_tax'] = self._total(
                    rpl_unit_price, nr_of_units_required)
                price_data['tpl_price_incl_tax'] = self._total(
                    tpl_unit_price, nr_of_units_required)

                # These are already quantized
                price_data['rpl_unit_price_incl_tax'] = rpl_unit_price
                price_data['tpl_unit_price_incl_tax'] = tpl_unit_price

                result.add(quantity, price_data)
        result.add_price_history(rpl_price_history, tpl_price_history)
        return result


class OptionsCalculator(BaseOptionsCalculator):
    pass
