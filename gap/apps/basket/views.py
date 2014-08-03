from oscar.apps.basket.views import BasketView as CoreBasketView
from apps.basket.forms import BasketLineForm

class BasketView(CoreBasketView):
    form_class = BasketLineForm
    pass
