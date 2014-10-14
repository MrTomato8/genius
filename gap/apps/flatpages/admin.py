from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from geniusautoparts.settings import TINYMCE_PATH


class TinyMCEAdmin(FlatPageAdmin):
    class Media:
        js = TINYMCE_PATH


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEAdmin)


