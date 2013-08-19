from django.contrib import admin
from apps.globals.models import Globals

class GlobalsAdmin(admin.ModelAdmin):
    list_display = 'tax',

admin.site.register(Globals, GlobalsAdmin)
