from oscar.apps.basket.forms import BasketLineForm as CoreBasketLineForm

class BasketLineForm(CoreBasketLineForm):
    class Meta:
        model = Line
        exclude = (
           'basket', 'product', 'line_reference',
           'price_excl_tax', 'price_incl_tax',
           'stockrecord_source'
        )
