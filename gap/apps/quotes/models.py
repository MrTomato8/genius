from django.db import models
from apps.options.calc import OptionsCalculator, PriceNotAvailable
from django.contrib.auth.models import User
from apps.options.models import OptionChoice
import json

Product = models.get_model('catalogue', 'Product')


class Quote(models.Model):
    caption = models.CharField(max_length=30, blank=True)
    user = models.ForeignKey(User, related_name='quotes')
    product = models.ForeignKey(Product)
    choices = models.ManyToManyField(OptionChoice, blank=True)
    quantity = models.PositiveIntegerField()
    choice_data = models.CharField(max_length=255, default='', blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{0} by {1}'.format(self.caption, self.user)

    class Meta:
        ordering = ['-date_added']

    def is_valid(self):
        calc = OptionsCalculator(self.product)
        prices = calc.calculate_costs(
            list(self.choices.all()), self.quantity, json.loads(self.choice_data))
        try:
            prices.get_price_incl_tax(self.quantity, self.user)
        except PriceNotAvailable:
            return False

        return True

    def price(self):
        calc = OptionsCalculator(self.product)
        prices = calc.calculate_costs(
            list(self.choices.all()), self.quantity, json.loads(self.choice_data))
        return prices.get_price_incl_tax(self.quantity, self.user)
