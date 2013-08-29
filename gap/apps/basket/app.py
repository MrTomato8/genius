from oscar.apps.basket.app import BasketApplication as CoreBasketApplication
from apps.basket import views

class BasketApplication(CoreBasketApplication):
    summary_view = views.BasketView
    pass
application = BasketApplication()
