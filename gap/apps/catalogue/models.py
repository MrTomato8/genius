from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractCategory
from oscar.apps.catalogue.abstract_models import AbstractProduct


class Category(AbstractCategory):
    @models.permalink
    def get_absolute_url(self):
        products = Product.objects.filter(categories=self)
        if products.count() == 1:
            return ('options:pick', (), {
                'product_slug': products[0].slug,
                'pk': products[0].id})
        return ('catalogue:category', (), {
                'category_slug': self.slug})


class Product(AbstractProduct):
    @models.permalink
    def get_absolute_url(self):
        return ('options:pick', (), {
                'product_slug': self.slug,
                'pk': self.id})

from oscar.apps.catalogue.models import *
