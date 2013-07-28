from apps.options.models import OptionPicker, ArtworkItem
from apps.quotes.models import Quote
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


class QuoteSaveForm(forms.Form):
    reference = forms.CharField(
        max_length=30,
        required=False,
        label='Reference to save (Optional)')

class QuoteChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.caption


class QuoteLoadForm(forms.Form):
    quote = QuoteChoiceField(
        queryset=Quote.objects.none(),
        required=True,
        label='Reference')

    def __init__(self, user, product, *args, **kwargs):
        super(QuoteLoadForm, self).__init__(*args, **kwargs)
        self.fields['quote'].queryset = Quote.objects.filter(
            user=user.pk, product=product.pk)


class ArtworkDeleteForm(forms.Form):
    pass


class ArtworkUploadForm(forms.ModelForm):
    class Meta:
        model = ArtworkItem
        fields = ['image']
