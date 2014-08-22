from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.apps.catalogue.abstract_models import AbstractCategory
from oscar.apps.catalogue.abstract_models import AbstractProduct
from oscar.apps.catalogue.abstract_models import AbstractOption


class Category(AbstractCategory):
    @models.permalink
    def get_absolute_url(self):
        products_count = getattr(self, 'products_count', None) # populated in my_category_tags
        if products_count is None:
            products_count = Product.objects.filter(categories=self).count()
        if products_count == 1:
            product = Product.objects.filter(categories=self)[:1].get()
            return ('options:pick', (), {
                'product_slug': product.slug,
                'pk': product.id})
        return ('catalogue:category', (), {
                'category_slug': self.slug})


class Product(AbstractProduct):
    short_title = models.CharField(_('Short title'), max_length=255, blank=True, null=True)
    @models.permalink
    def get_absolute_url(self):
        return ('options:pick', (), {
                'product_slug': self.slug,
                'pk': self.id})


class Option(AbstractOption):
    short_description_weight = models.PositiveSmallIntegerField(_('Short description weight'),
                                                                blank=True, null=True, default=0)


from oscar.apps.catalogue.models import *
