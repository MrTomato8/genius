from django.contrib import admin
from apps.options.models import OptionPicker, OptionPickerGroup, OptionChoice
from apps.options.models import ArtworkItem
from django.db import models
from django import forms

Option = models.get_model('catalogue', 'Option')


class OptionPickerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OptionPickerForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            pickers = OptionPicker.objects.exclude(option=self.instance.option)
        else:
            pickers = OptionPicker.objects.all()

        opts = map(lambda x: x.option.pk, pickers)

        self.fields['option'].queryset = Option.objects.exclude(pk__in=opts)


class OptionPickerAdmin(admin.ModelAdmin):
    form = OptionPickerForm
    
    

class OptionChoiceAdmin(admin.ModelAdmin):
    filter_horizontal = ('conflicts_with',)
    search_fields =('code',)
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('code',)
        return self.readonly_fields

admin.site.register(OptionPicker, OptionPickerAdmin)
admin.site.register(OptionPickerGroup)
admin.site.register(OptionChoice, OptionChoiceAdmin)
admin.site.register(ArtworkItem)
