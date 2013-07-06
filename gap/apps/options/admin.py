from django.contrib import admin
from apps.options.models import OptionPicker, OptionPickerGroup
from django.db import models
from django import forms

Option = models.get_model('catalogue', 'Option')


class OptionPickerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OptionPickerForm, self).__init__(*args, **kwargs)

        opts = map(lambda x: x.option.pk,
                   OptionPicker.objects.exclude(option=self.instance.option))

        self.fields['option'].queryset = Option.objects.exclude(pk__in=opts)


class OptionPickerAdmin(admin.ModelAdmin):
    form = OptionPickerForm


admin.site.register(OptionPicker, OptionPickerAdmin)
admin.site.register(OptionPickerGroup)
