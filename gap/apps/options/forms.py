from apps.options.models import OptionPicker, ArtworkItem
from django import forms


class OptionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.caption


def picker_form_factory(product, picker, choices):
    if picker.widget == OptionPicker.THUMBNAIL:
        widget = forms.widgets.RadioSelect
    elif picker.widget == OptionPicker.DROPDOWN:
        widget = forms.widgets.Select

    properties = {
        'choice_errors': [],
        picker.option.code: OptionChoiceField(
            widget=widget,
            empty_label=None,
            queryset=choices)
    }

    return type(
        str(''.join([picker.option.code, 'Form'])),
        (forms.Form,),
        properties)


class QuoteCalcForm(forms.Form):
    quantity = forms.IntegerField()


class QuoteCustomSizeForm(forms.Form):
    width = forms.IntegerField()
    height = forms.IntegerField()


class ArtworkDeleteForm(forms.Form):
    pass


class ArtworkUploadForm(forms.ModelForm):
    class Meta:
        model = ArtworkItem
        fields = ['image']
