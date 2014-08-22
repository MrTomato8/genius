# -*- coding: utf-8 -*-
from decimal import Decimal #, ROUND_UP
from collections import OrderedDict
#from math import ceil
from django.conf import settings

from apps.options import utils

from .exceptions import PriceNotAvailable
TWOPLACES = Decimal(10) ** -2
THREEPLACES=Decimal(10) ** -3

class CalculatedPrices(object):
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

    def _get_price_attribute(self, quantity, number_of_files, user, attribute):
        if utils.trade_user(user):
            prefix = 'tpl_'
        else:
            prefix = 'rpl_'

        '''
        sheet_type = False  # lint:ok
        selected_quantity = 0
        found = False
        units_multiplier = Decimal('1')
        price_multiplier = Decimal('1')
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
        '''
        '''
        if self.discrete_pricing:
            for key in self._prices:
                if key == quantity:
                    selected_quantity= key
                    break
                if key > selected_quantity and key < quantity:
                    selected_quantity= key
            if selected_quantity == 0:
                raise PriceNotAvailable
            price_multiplier = selected_quantity or quantity
        quantity = selected_quantity or quantity
        '''
        try:
            prices = self._prices[quantity]
        except:
            raise PriceNotAvailable, 'quantity %s not found'%quantity

        try:
            # sometimes number of files can be zero (is line has no attachments yet, for example)
            number_of_files = number_of_files or 1
            tpl = (
                prices[prefix + attribute] + settings.MULTIFILE_PRICE_PER_ADDITIONAL_FILE * (number_of_files - 1),
                prices['nr_of_units'],
                prices['items_per_pack'])

            return tpl
        except:
            raise PriceNotAvailable

    def get_unit_price_incl_tax(self, quantity, number_of_files, user):
        return self._get_price_attribute(quantity, number_of_files, user, 'unit_price_incl_tax')

    def get_price_incl_tax(self, quantity, number_of_files, user):
        return self._get_price_attribute(quantity, number_of_files, user, 'price_incl_tax')

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
        dikt = {'price':selected[0], 'items_per_pack':selected[1]}
        return dikt

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
        dikt = {'price':selected[0], 'items_per_pack':selected[1]}
        return dikt
