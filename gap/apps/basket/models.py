from django.db import models

from oscar.apps.basket.abstract_models import (
    AbstractBasket, AbstractLine, AbstractLineAttribute)

class Basket(AbstractBasket):
    pass


class Line(AbstractLine):
    pass



from oscar.apps.basket.models import *
