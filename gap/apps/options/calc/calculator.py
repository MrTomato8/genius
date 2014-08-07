# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_HALF_UP, ROUND_UP
import zlib
from math import ceil, floor
from django.db.models import  Max #, Min
from django.core.exceptions import ObjectDoesNotExist

from apps.options import utils

from . import CalculatedPrices
from .cache import CalcCache
from .exceptions import NotEnoughArguments,DuplicateQuantities, TooSmall,TooLow

TWOPLACES = Decimal(10) ** -2
THREEPLACES=Decimal(10) ** -4
CUSTOM=[
    False,
    'linear',
    'area',
    ]
class BaseOptionsCalculator(object):

    key = None

    def __init__(self, product):
        self.product = product
        self.quantize = TWOPLACES
        self.current_coiches = None

    def get_key(self,choices, choice_data, quantity=None):
        self.key = self.key or zlib.crc32(str(choices)+str(choice_data)+str(quantity))
        return self.key

    def _get_area(self, choice_data):
        #TODO: Refactoring custom
        result = 0

        try:
            cargs = choice_data[utils.custom_size_option_name()]
        except KeyError:
            raise NotEnoughArguments(
                'choice_data argument does not contain {0} key'.format(
                    utils.custom_size_option_name()))

        if 'width' in cargs and 'height' in cargs:
            # calculate area in square metres
            area = Decimal(cargs['width'] * cargs['height'])

            result = area

        else:
            raise NotEnoughArguments('For custom size width and height'
                                     'should be supplied')

        return result
    def get_row(self, media, choice_data):
        def calculate(media,width,height):
            # calculate number of rows
            width_mod  = media%width
            height_mod = media%height
            if height_mod == width_mod !=0:
                return False,0
            if width_mod==0:
                fitter, unfitter = width, height
            elif height_mod==0:
                fitter, unfitter=height, width
            else:
                if min(width_mod,height_mod)==width_mod:
                     fitter, unfitter = width, height
                else:
                     fitter, unfitter = height, width
            return int(floor(media/fitter)), unfitter

        try:

            cargs = choice_data[utils.custom_size_option_name()]
            width=Decimal(cargs['width'])
            height=Decimal(cargs['height'])
        except KeyError:
            raise NotEnoughArguments(
                'choice_data argument does not contain {0} key'.format(
                    utils.custom_size_option_name()))

        media_number=1
        row, length = calculate(media,width,height)

        while row is False:
            media_number +=1
            row, length = calculate(media*media_number,width,height)
        return media_number, row, length



    def custom_calc(self, prices, choice_data, quantity=None):
        if prices[0].min_length!=Decimal(0):
            try:
                media_number, items_per_row, row_height = self.get_row(
                    prices[0].media_width, choice_data)
            except Exception:
                return prices, Decimal(1), 2
            total = media_number*row_height*int(ceil(quantity/Decimal(items_per_row)))
            try:
                    price = prices.filter(min_length__lte=total).order_by('-min_area')[0]
            except:
                raise TooSmall('too small')
        else:
            try:
                total = self._get_area(choice_data)*quantity
            except Exception:
                return prices, Decimal(1), 2
            if not total:
                return prices, Decimal(1), 2
            try:
                price = prices.filter(min_area__lte=total).order_by('-min_area')[0]
            except:
                raise TooSmall('too small')
        return price, total, 0

    def quantity_calc(self, prices, choice_data):
        min_order_max = prices.aggregate(Max('min_order'))['min_order__max']
        prices = prices.filter(min_order=min_order_max)
        count = prices.values('quantity').count()
        distinct = prices.values('quantity').distinct().count()
        # Abort if duplicate quantities found in discrete priced product.
        if (int(prices.values('quantity').count()) > int(distinct)):
            import pprint
            txt='\n'
            txt += str(distinct)+'\n'
            txt += str(count)+'\n'
            txt += pprint.pformat(choice_data)
            raise DuplicateQuantities('Look for invalid lines in pricelist'+txt)
        return prices, distinct

    def pick_prices(self, choices, choice_data, quantity=None):
        '''
        Picks Price objects which statisfy given quantity
        and choice selections
        '''

        self.key = self.get_key(choices, choice_data, quantity)
        prices = CalcCache.add(self.key, 'prices', False)
        if prices:
            # cut off everithing else and return cache
            discrete = CalcCache.get(self.key, 'discrete')
            length = CalcCache.get(self.key, 'length')
            return prices, discrete, length
        prices = self.product.prices.all()
        # Keep prices for selected options only
        for choice in choices:prices = prices.filter(option_choices=choice)
        if quantity is not None:
            prices = prices.filter(min_order__lte=quantity)
            try:
                prices[0]
            except:
                raise TooLow

        custom_size = utils.custom_size_chosen(choices)
        distinct = 0
        length=Decimal(1)
        if custom_size:
            prices, length, distinct = self.custom_calc(prices, choice_data, quantity)
        else:
            prices, distinct = self.quantity_calc(prices, choice_data)

        #it doesn't have sense to consider discrete if custom is active
        discrete = distinct > 1
        CalcCache.set(self.key, 'prices', prices)
        CalcCache.set(self.key, 'discrete', discrete)
        CalcCache.set(self.key, 'length', length)
        # Return prices for all found discrete quantities

        return prices, discrete, length

    def _apply_choice_data(self, price, choices, choice_data):
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

    def get_small_things(self, price, result):
        '''
            this is inded hacky so let explain it
            1)
            This means that the quantity in price is less than items per pack
            for at least one price so this mean that quantity refer to a pack
            2)
            Now we double check our hipotesis since the price is for
            some reason referred to a item in a pack, meaning that its
            price has three decimal places
        '''
        if price.quantity<price.items_per_pack:
            result.matrix_for_pack = True

        two_place_rpl = price.rpl_price.quantize(TWOPLACES)
        three_place_rpl = price.rpl_price.quantize(THREEPLACES)
        if (not result.triple_decimal and two_place_rpl != three_place_rpl):
            result.triple_decimal = True

        return None

    def calc_small_things(self,price, quantity, rpl,tpl):
        #quantity means the number of packs,
        #items per pack means the number of things in a pack
        #nr_of_units is the number of items
        self.quantize = THREEPLACES #this is used by _unit() and _total()
        rpl = rpl * quantity
        tpl = tpl * quantity
        if rpl < price.min_rpl_price:
            rpl = price.min_rpl_price
        if tpl < price.min_tpl_price:
            tpl = price.min_tpl_price

        nr_of_units = quantity*price.items_per_pack
        return rpl, tpl,  nr_of_units, quantity#same mean for small and big

    def calc_big_things(self,price, quantity, rpl,tpl):
        # quantity is the number of items
        # items per pack is self explanatory
        # nr of units means the number of packs
        if quantity is not None:
            nr_of_units = self._calc_units(
                price.items_per_pack, quantity)
        else:
            nr_of_units=1
        rpl = rpl*nr_of_units
        tpl = tpl*nr_of_units
        if rpl< price.min_rpl_price:
            rpl = price.min_rpl_price

        if tpl < price.min_tpl_price:
            tpl = price.min_tpl_price
        return rpl,tpl,nr_of_units, quantity#same mean for small and big

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
        if quantity: quantity=int(quantity)
        self.key = self.get_key(choices, choice_data, quantity)
        result = CalcCache.get(self.key, 'result', None)
        if result is not None:
            return result
        result = CalculatedPrices()

        if choice_data is None:
            choice_data = {}

        prices, discrete, length = self.pick_prices(choices, choice_data, quantity)
        # vanilla price history
        rpl_history = []
        tpl_history = []
        # Discrete pricing scheme
        if discrete and (quantity == 0 or quantity<=min([price.quantity for price in prices])):
            quantity = None
        if discrete:
            prc=prices[0]
            result.discrete_pricing = True
            for price in prices:
                self.get_small_things(price, result)
                if result.triple_decimal and result.matrix_for_pack:
                    break
            if not result.matrix_for_pack: result.triple_decimal=False
            for price in prices:
                price_data = {}
                rpl = self._apply_choice_data(
                    price.rpl_price, choices, choice_data)
                tpl = self._apply_choice_data(
                    price.tpl_price, choices, choice_data)
                qty = price.quantity
                rpl_history.append((price.rpl_price, price.items_per_pack))
                tpl_history.append((price.tpl_price, price.items_per_pack))
                b = result.triple_decimal and result.matrix_for_pack
                if b:
                    rpl,tpl,nr_of_units,qty= self.calc_small_things(
                        price,qty,rpl,tpl)
                else:
                    rpl,tpl,nr_of_units,qty = self.calc_big_things(
                        price, qty, rpl,tpl)
                rpl_unit_price = self._unit(rpl, nr_of_units)
                tpl_unit_price = self._unit(tpl, nr_of_units)

                price_data['items_per_pack'] = price.items_per_pack
                price_data['rpl_price_incl_tax'] = self._total(
                    rpl_unit_price, nr_of_units)
                price_data['tpl_price_incl_tax'] = self._total(
                    tpl_unit_price, nr_of_units)
                price_data['nr_of_units']=nr_of_units
                price_data['tpl_price'] = tpl
                price_data['rpl_price'] = rpl
                # These are already quantized
                price_data['rpl_unit_price_incl_tax'] = rpl_unit_price
                price_data['tpl_unit_price_incl_tax'] = tpl_unit_price
                result.add(qty, price_data)
                if b:
                    if  quantity >= nr_of_units and  price.quantity >prc.quantity:
                        prc = price
                else:
                    if quantity >= price.quantity>prc.quantity:
                        prc = price
            if quantity:
                rpl = self._apply_choice_data(
                    prc.rpl_price, choices, choice_data)
                tpl = self._apply_choice_data(
                    prc.tpl_price, choices, choice_data)
                if b:
                    rpl,tpl,nr_of_units,qty= self.calc_small_things(
                        prc,int(ceil(Decimal(quantity)/prc.items_per_pack)),rpl,tpl)
                else:
                    rpl,tpl,nr_of_units,qty = self.calc_big_things(
                        prc, quantity, rpl,tpl)

                rpl_unit_price = self._unit(rpl, nr_of_units)
                tpl_unit_price = self._unit(tpl, nr_of_units)
                price_data['items_per_pack'] = prc.items_per_pack
                price_data['rpl_price_incl_tax'] = self._total(
                    rpl_unit_price, nr_of_units)
                price_data['tpl_price_incl_tax'] = self._total(
                    tpl_unit_price, nr_of_units)
                price_data['nr_of_units']=nr_of_units
                price_data['tpl_price'] = tpl
                price_data['rpl_price'] = rpl
                # These are already quantized
                price_data['rpl_unit_price_incl_tax'] = rpl_unit_price
                price_data['tpl_unit_price_incl_tax'] = tpl_unit_price
                result.add(quantity, price_data)

        else:
            result.discrete_pricing = False
            try:
                price = prices.get()
            except ObjectDoesNotExist:
                return result
            except AttributeError:
                if not prices is None:
                    price = prices

            if quantity is not None:
                #Refactor custom : surelly we should work here for multiline
                rpl_history.append((price.rpl_price, price.items_per_pack))
                tpl_history.append((price.tpl_price, price.items_per_pack))

                rpl = self._apply_choice_data(
                    price.rpl_price, choices, choice_data)*length
                tpl = self._apply_choice_data(
                    price.tpl_price, choices, choice_data)*length
                items_per_pack = price.items_per_pack
                nr_of_units = self._calc_units(
                    items_per_pack, quantity)

                nr_of_units_required = self._calc_units(
                    items_per_pack, quantity)
                rpl_unit_price = self._unit(rpl, nr_of_units)
                tpl_unit_price = self._unit(tpl, nr_of_units)
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
        result.add_price_history(rpl_history, tpl_history)
        CalcCache.set(self.key, 'result',result)
        return result

class OptionsCalculator(BaseOptionsCalculator):
    pass
