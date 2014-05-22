from django.db.models import Min, Max
from apps.options import utils
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
from django.core.exceptions import ObjectDoesNotExist
from collections import OrderedDict
from math import ceil
import zlib
TWOPLACES = Decimal(10) ** -2
THREEPLACES=Decimal(10) ** -3


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
        self.matrix_for_pack = False
        self.discrete_pricing = False
        self.triple_decimal = False
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
        units_multiplier = Decimal('1')
        price_multiplier = Decimal('1')

        sheet_type = False
        selected_quantity = 0
        found = False
        
        if self.matrix_for_pack:
            for key in self._prices:
                price = self._prices[key]
                nr_of_items = (Decimal(quantity) / Decimal(price['items_per_pack'])).quantize(Decimal('1.'), rounding=ROUND_UP)
                if key == nr_of_items:
                    selected_quantity = key
                    break
                elif key > selected_quantity and key < nr_of_items:
                    selected_quantity = key
            
            #units_multiplier= Decimal(nr_of_items)
            #price_multiplier = Decimal(ceil(nr_of_items/Decimal(selected_quantity)))
        elif self.discrete_pricing:
            for key in self._prices:
                if key == quantity:
                    selected_quantity= key
                    found = True
                elif not found and key > selected_quantity and key < quantity:
                    selected_quantity= key
            if selected_quantity == 0:
                raise PriceNotAvailable
            # It should be 1, if not we will fix it
            units_multiplier = Decimal(ceil(quantity/Decimal(selected_quantity)))
            price_multiplier = quantity
        if selected_quantity != 0:
            quantity = selected_quantity
        try:
            prices = self._prices[quantity]
        except:
            raise PriceNotAvailable, 'quantity %s not found'%quantity
        
        if self.triple_decimal and self.matrix_for_pack:
            #this has sense since quantity will be set to 1
            price_multiplier = nr_of_items
            pass
        else:
            self.triple_decimal = False
        try:

            tuple = (
                prices[prefix + attribute]*price_multiplier,
                prices['nr_of_units']*units_multiplier,
                prices['items_per_pack'])
            
            return tuple
        except:
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
        selected = None
        for price in self.vanilla_rpl_prices:
            if selected is None:
                selected = price
            else:
                if price[0] and price[0]<selected[0]:
                    price = selected
                elif price[0]==selected[0] and price[1]>selected[1]:
                    price = selected
                pass                
        dict = {'price':selected[0], 'items_per_pack':selected[1]}
        return dict
    
    def get_min_tpl_price(self):
        selected = None
        for price in self.vanilla_tpl_prices:
            if selected is None:
                selected = price
            else:
                
                if price[0] and price[0]<selected[0]:
                    price = selected
                elif price[0]==selected[0] and price[1]>selected[1]:
                    price = selected
                pass
        dict = {'price':selected[0], 'items_per_pack':selected[1]}
        return dict

class CalcCache(object):
    dict = {}
    @classmethod
    def create(cls, p):
        r = cls.dict.has_key(p)
        if not r:
            r = cls.dict[p] = {}
    @classmethod
    def get(cls, p, key, default = None):
        cls.create(p)
        return cls.dict[p].get(key, None)
    @classmethod
    def set(cls, p, key, value):
        cls.create(p)
        cls.dict[p][key]= value
        return cls.dict[p][key]
    
    @classmethod
    def get_or_set(cls, p, key, default = None):
        cls.create(p)
        r = cls.get(p, key)
        if not r:
            r = cls.set(p, key, default)
        return cls.get(p, key)

class BaseOptionsCalculator:
    cache = {}
    def __init__(self, product):
        self.product = product
        self.quantize = TWOPLACES
        self.current_coiches = None
        
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
        
        self.current_choices = zlib.crc32(str(choices)+str(choice_data)+str(quantity))
        prices = CalcCache.get_or_set(self.current_choices, 'prices', False)
        if prices:
            return prices, CalcCache.get(self.current_choices, 'discrete')
        prices = self.product.prices.all()
        
        custom_size = utils.custom_size_chosen(choices)
        
        if quantity is not None:
            prices = prices.filter(min_order__lte=quantity)

        if custom_size:
            area = self._get_area(choice_data)
            prices = prices.filter(min_area__lte=area)
        # Keep prices for selected options only
        for choice in choices:
            prices = prices.filter(option_choices=choice)
            
        discrete = prices.values('quantity').distinct().count() > 1
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
        CalcCache.set(self.current_choices, 'prices', prices)
        CalcCache.set(self.current_choices, 'discrete', discrete)
        # Return prices for all found discrete quantities
        
        return prices, discrete

    def _apply_choice_data(self, price, choices, choice_data):
        size_chosen = CalcCache.get(self.current_choices, 'custom_size', None)
        if size_chosen is None:
            CalcCache.set(self.current_choices, 'custom_size', utils.custom_size_chosen(choices))
            size_chosen = CalcCache.get(self.current_choices, 'custom_size', None)           
        if size_chosen:
            area = self._get_area(choice_data)
            CalcCache.set(self.current_choices, 'area',area)
            return price*area
        #elif ... More transformations may be added here in the future
        else:
            return price

    def _calc_units(self, items_per_pack, quantity):
        #there was this line
        # if items_per_pack == 1: return 1
        if items_per_pack == quantity:
            return 1
        if items_per_pack == 1:
            return quantity
        return (Decimal(quantity) / Decimal(items_per_pack)).quantize(
            Decimal('1.'), rounding=ROUND_UP)

    def _total(self, price, quantity):
        return (price * quantity).quantize(self.quantize, ROUND_HALF_UP)
        
    def _unit(self, price, quantity):
        return (price / quantity).quantize(self.quantize, ROUND_HALF_UP)

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
        self.current_choices = zlib.crc32(str(choices)+str(choice_data)+str(quantity))
        prices = CalcCache.get_or_set(self.current_choices, 'prices', False)
        result = CalcCache.get(self.current_choices, 'result', None)
        if result is not None:
            return result
        result = CalculatedPrices()
        matrix_for_pack = False
        
        if choice_data is None:
            choice_data = {}

        if quantity == 0:
            quantity = None
            
        prices, discrete = self.pick_prices(choices, choice_data, quantity)
        # vanilla price history
        rpl_price_history = []
        tpl_price_history = []
        
        # Discrete pricing scheme
        if discrete:
            result.discrete_pricing = True
            for price in prices:
                if price.quantity<price.items_per_pack:
                    matrix_for_pack = result.matrix_for_pack = True
                if ( not result.triple_decimal and
                    price.rpl_price.quantize(THREEPLACES) != price.rpl_price.quantize(TWOPLACES) 
                    or
                    price.tpl_price.quantize(THREEPLACES) != price.tpl_price.quantize(TWOPLACES)
                    ):
                    result.triple_decimal = True
                    self.quantize = THREEPLACES
                if result.triple_decimal and matrix_for_pack:
                    break
            for price in prices:
                rpl_price_history.append((price.rpl_price, price.items_per_pack))
                tpl_price_history.append((price.tpl_price, price.items_per_pack))
                
                rpl_price = self._apply_choice_data(
                    price.rpl_price, choices, choice_data)
                tpl_price = self._apply_choice_data(
                    price.tpl_price, choices, choice_data)
                
                items_per_pack = price.items_per_pack
                if not matrix_for_pack and quantity is not None:
                    nr_of_units = self._calc_units(
                        items_per_pack, quantity)
                elif quantity is None:
                    nr_of_units = self._calc_units(
                        items_per_pack, price.quantity)
                else:
                    nr_of_units=1
                if matrix_for_pack:
                    if rpl_price*price.quantity < price.min_rpl_price:
                        rpl_price = price.min_rpl_price
    
                    if tpl_price*price.quantity < price.min_tpl_price:
                        tpl_price = price.min_tpl_price
                else:    
                    if rpl_price*nr_of_units < price.min_rpl_price:
                        rpl_price = price.min_rpl_price
    
                    if tpl_price*nr_of_units < price.min_tpl_price:
                        tpl_price = price.min_tpl_price
                rpl_unit_price = self._unit(rpl_price, nr_of_units)
                tpl_unit_price = self._unit(tpl_price, nr_of_units)

                price_data = {}

                
                price_data['items_per_pack'] = items_per_pack

                price_data['rpl_price_incl_tax'] = self._total(
                    rpl_unit_price, nr_of_units)
                price_data['tpl_price_incl_tax'] = self._total(
                    tpl_unit_price, nr_of_units)
                price_data['nr_of_units']=nr_of_units
                price_data['tpl_price'] = tpl_price
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
                
                rpl_price_history.append((price.rpl_price, price.items_per_pack))
                tpl_price_history.append((price.tpl_price, price.items_per_pack))
                
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
        CalcCache.set(self.current_choices, 'result',result)
        return result


class OptionsCalculator(BaseOptionsCalculator):
    pass
