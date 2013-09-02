from decimal import Decimal as D, ROUND_UP
from oscar.apps.partner import wrappers

TWOPLACES = D(10) ** -2


class DefaultWrapper(wrappers.DefaultWrapper):
    def __init__(self, tax_percent=None, **kwargs):
        if tax_percent is None:
            self.tax_percent = D('0.000')
        else:
            self.tax_percent = tax_percent
        super(DefaultWrapper, self).__init__(**kwargs)

    def get_tax(self, price):
        return (price * self.tax_percent).quantize(TWOPLACES, ROUND_UP)

    def calculate_tax(self, stockrecord):
        price_excl_tax = stockrecord.price_excl_tax
        return self.get_tax(price_excl_tax)

    def get_total_price_incl_tax(self, price_excl_tax):
        tax = self.get_tax(price_excl_tax)
        price_excl_tax = price_excl_tax + tax
        return price_excl_tax

