from oscar.apps.basket.forms import BasketLineForm as CoreBasketLineForm
from apps.basket.models import Line

class BasketLineForm(CoreBasketLineForm):
    class Meta:
        model = Line
        exclude = (
           'basket', 'product', 'line_reference',
           'price_excl_tax', 'price_incl_tax',
           'stockrecord_source','real_quantity',
           'items_required'
        )
    def clean(self):
        cleaned_data = super(BasketLineForm,self).clean()
        return cleaned_data
