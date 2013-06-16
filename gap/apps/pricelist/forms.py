from django import forms


class PricelistUploadForm(forms.Form):
    csvfile = forms.FileField(label='CSV File')
