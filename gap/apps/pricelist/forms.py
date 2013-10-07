from django import forms


class PricelistUploadForm(forms.Form):
    csvfile = forms.FileField(label='CSV File')
    create_options = forms.BooleanField(
        required=False,
        label='Allow creation of missing options')
    create_choices = forms.BooleanField(
        required=False,
        label='Allow creation of missing option choices')
    chirurgical = forms.BooleanField(
        required=False,
        label='Selective load of pricelist',
        initial=True)