from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings
''' !!! WTF !!! '''

class Globals(models.Model):
    #It's nonsense should at least have a country field
    tax = models.DecimalField(_('VAT (percent as decimal)'), decimal_places=3,
        max_digits=12, default=Decimal('0.000'), help_text=_(
            "Example: for 20% set 0.20 here, for 18,5% set 0.185")
        )

    class Meta:
        verbose_name=u'Globals'
        verbose_name_plural=u'Globals'


def get_tax_percent():
    try:
        return settings.TAX
    except IndexError:
        return Decimal('0.00')
