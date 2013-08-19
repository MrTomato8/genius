from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext as _


class Globals(models.Model):
    tax = models.DecimalField(_('VAT (percent as decimal)'), decimal_places=3,
        max_digits=12, default=Decimal('0.000'), help_text=_(
            "Example: for 20% set 0.20 here, for 18,5% set 0.185")
        )

    class Meta:
        verbose_name=u'Globals'
        verbose_name_plural=u'Globals'


def get_tax_percent():
    # TODO: get from cache
    try:
        return Globals.objects.all()[0].tax
    except IndexError:
        return Decimal('0.000')
