from django.contrib import admin
from apps.catalogue.models import Category, Product
from geniusautoparts.settings import TINYMCE_PATH


class CategoryAdmin(admin.ModelAdmin):
    class Media:
        js = TINYMCE_PATH


class ProductAdmin(admin.ModelAdmin):
    class Media:
        js = TINYMCE_PATH


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
