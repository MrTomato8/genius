# -*- coding: utf-8 -*-
from decimal import Decimal

from math import ceil, floor

from django.conf import settings

from apps.options import utils

from .exceptions import NotEnoughArguments,DuplicateCSV

class BaseOptionsCalculator(object):
    '''
        All prices in calculator are Tax Free
        as it does know nothing about Taxes
    '''
    total = {}
    custom = False
    price = None
    discount = None
    total = None
    def __init__(self, product,choices,data):
        self.product = product
        self.choices = choices
        self.data=data
        self.pick_price()
        self.custom = self.size_is_custom()
        self.quantity = self.data.get('quantity',None)

    def size_is_custom(self):
        return utils.custom_size_chosen(self.choices)

    def get_custom_vars(self):
        try:
            width=Decimal(self.data.get('width'))/1000
            height=Decimal(self.data.get('height'))/1000
        except KeyError:
            raise NotEnoughArguments(
                'custom size argument does not contain {0} key'.format(
                    utils.custom_size_option_name()))
        return width,height

    def get_area(self):
        width,height =self.get_custom_vars()
        return width*height

    def get_row(self):
        media = self.price.media_width
        def calculate(media,width,height):
            # calculate number of rows
            if media < width and media < height:
                return False,0
            width_mod  = media%width
            height_mod = media%height
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

        width,height =self.get_custom_vars()

        media_number=1
        items_per_row, row_height = calculate(media,width,height)

        while items_per_row is False:
            media_number +=1
            items_per_row, row_height = calculate(media*media_number,width,height)

        #row area in self.price.media_width units
        row_area = media_number*row_height
        return row_area, items_per_row



    def calculate_custom(self):

        if self.total:
            return self.total

        #exception = TooSmall('too small, increase the number of items or their area')

        if self.price.min_length!=Decimal(0):
            try:
                row_area, items_per_row = self.get_row()
            except Exception:
                return NotEnoughArguments(
                'choice_data argument does not contain {0} key'.format(
                    utils.custom_size_option_name()))
            total = row_area/ceil(self.quantity/Decimal(items_per_row))

            if self.price.min_length > total:
                return False
        else:
            total = self.get_area()*self.quantity

            if self.price.min_area>total:
                return False

        self.total=total
        return total


    def pick_price(self):
        '''
        Picks Price objects which statisfy given quantity
        and choice selections
        '''
        if self.price:
            return self.price
        prices = self.product.prices.all()

        for choice in self.choices:prices = prices.filter(option_choices=choice)
        if len(prices)>1:
            raise DuplicateCSV('Duplicated Csv lines')
        price = prices[0]
        self.price = price

    def get_custom_anomaly(self):
        if self.custom:
            return self.calculate_custom()
        return False

    def get_discount(self):
        if self.discount:
            return self.discount
        if self.custom:
            quantity = self.calculate_custom()
        else:
            quantity = self.quantity
        try:
            discount = self.price.discounts.filter(quantity__lte=quantity)[0].discount
            self.discount = discount
            return discount
        except:
            return False

    def is_tpl(self,user):
        if user is None:return False
        return user.groups.all().filter(name=settings.TRADE_GROUP_NAME).exists()

    def check_quantity(self):
        price = self.price
        if self.custom:
            if not bool(self.calculate_custom()):return False
        elif price.min_order>self.quantity:
            return False
        if self.get_discount() is False:return False

        return True

    def unit_price_without_discount(self,user):
        return self.is_tpl(user) and self.price.tpl_price or self.price.rpl_price

    def multifile_price(self):
        number_of_files=self.data['number_of_files']
        return settings.MULTIFILE_PRICE_PER_ADDITIONAL_FILE * (number_of_files) or 1

    def price_per_unit(self,user):
        '''
            price per unit with discount
        '''
        discount = self.get_discount()

        if discount is False:
            return False

        price = self.unit_price_without_discount(user)

        return price*(100-discount)/Decimal(100)+self.multifile_price()

    def total_price(self,user):
        '''
            total price with discount
        '''
        price_per_unit= self.price_per_unit(user)

        if not price_per_unit:return False

        if self.custom:
            quantity = self.calculate_custom()
        else:
            quantity = self.quantity

        return price_per_unit*Decimal(quantity)




class OptionsCalculator(BaseOptionsCalculator):
    pass
