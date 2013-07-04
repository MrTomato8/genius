from apps.options.models import OptionPicker
from django import forms


def picker_form_factory(product, picker, choices):
    if picker.widget == OptionPicker.THUMBNAIL:
        widget = forms.widgets.RadioSelect
    elif picker.widget == OptionPicker.DROPDOWN:
        widget = forms.widgets.Select

    properties = {
        picker.option.code: forms.ModelChoiceField(
            widget=widget,
            empty_label=None,
            queryset=choices)
    }

    return type(
        str(''.join([picker.option.code, 'Form'])),
        (forms.Form,),
        properties)
