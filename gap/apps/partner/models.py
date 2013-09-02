from decimal import Decimal as D
from apps.partner.wrappers import DefaultWrapper
from apps.globals.models import get_tax_percent


class StockRecordForChoices(object):
    """
    Global stockrecord for OPTIONS_CALCULATOR type.
    """
    def __init__(self, price_excl_tax):
        self.price_excl_tax = price_excl_tax
        self.curr_tax_percent = get_tax_percent()

    @property
    def price_incl_tax(self):
        if self.price_excl_tax is None:
            return D('0.00')
        return self.price_excl_tax + self.price_tax

    @property
    def price_tax(self):
        """
        Return a product's tax value
        """
        return DefaultWrapper(self.curr_tax_percent).calculate_tax(self)

from oscar.apps.partner.models import *
