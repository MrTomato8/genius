from django.contrib import admin
from apps.options.models import OptionPicker, OptionPickerGroup
from django.db import models

Option = models.get_model('catalogue', 'Option')


class OptionPickerAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'option':
            opts = map(lambda x: x.option.pk,
                       OptionPicker.objects.all())

            kwargs['queryset'] = Option.objects.exclude(pk__in=opts)
        return super(OptionPickerAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

admin.site.register(OptionPicker, OptionPickerAdmin)
admin.site.register(OptionPickerGroup)
