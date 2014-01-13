from django.db import models
from django.db.models.loading import get_model
from django.contrib.auth.models import User

from oscar.apps.order.abstract_models import AbstractOrder, AbstractLine


SMALL_ORDER = "Small format digital"
LARGE_ORDER = "Large format digital"
EXHIBITION_ORDER = "Exhibition"

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')
Line = get_model('order', 'Line')

class SmallOrderManager(models.Manager):
    def get_query_set(self):
        qs = super(SmallOrderManager, self).get_query_set()
        small_category = Category.objects.get(name__iexact=SMALL_ORDER)
        small_categories = [small_category] + list(small_category.get_children())
        
        return qs.filter(lines__in=Line.objects.filter(product__categories__in=small_categories)).distinct()


class LargeOrderManager(models.Manager):
    def get_query_set(self):
        qs = super(LargeOrderManager, self).get_query_set()
        large_category = Category.objects.get(name__iexact=LARGE_ORDER)
        large_categories = [large_category] + list(large_category.get_children())
        
        return qs.filter(lines__in=Line.objects.filter(product__categories__in=large_categories)).distinct()


class ExhibitionOrderManager(models.Manager):
    def get_query_set(self):
        qs = super(ExhibitionOrderManager, self).get_query_set()
        exhibition_category = Category.objects.get(name__iexact=EXHIBITION_ORDER)
        exhibition_categories = [exhibition_category] + list(exhibition_category.get_children())
        
        return qs.filter(lines__in=Line.objects.filter(product__categories__in=exhibition_categories)).distinct()


class Order(AbstractOrder):
    objects = models.Manager()
    small = SmallOrderManager()
    large = LargeOrderManager()
    exhibition = ExhibitionOrderManager()

    def has_multiple_zones(self):
        def get_root_category(category):
            return category.get_root()

        products = Product.objects.filter(line__in=self.lines.all())
        categories = Category.objects.filter(product__in=products)
        root_categories = map(get_root_category, categories)
        return len(set(root_categories)) > 1

    def get_small_lines(self):
        small_category = Category.objects.get(name__iexact=SMALL_ORDER)
        small_categories = [small_category] + list(small_category.get_children())
        return self.lines.filter(product__categories__in=small_categories)

    def get_large_lines(self):
        large_category = Category.objects.get(name__iexact=LARGE_ORDER)
        large_categories = [large_category] + list(large_category.get_children())
        return self.lines.filter(product__categories__in=large_categories)

    def get_exhibition_lines(self):
        exhibition_category = Category.objects.get(name__iexact=EXHIBITION_ORDER)
        exhibition_categories = [exhibition_category] + list(exhibition_category.get_children())
        return self.lines.filter(product__categories__in=exhibition_categories)

from oscar.apps.order.models import *