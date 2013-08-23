from django.contrib import admin
from apps.pricelist.models import Price

class PriceAdmin(admin.ModelAdmin):
    filter_horizontal = ('option_choices',)

admin.site.register(Price, PriceAdmin)
