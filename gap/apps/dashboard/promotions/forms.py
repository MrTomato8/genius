from django import forms
from django_markdown.widgets import MarkdownWidget
from apps.promotions.models import RawHTML


class MarkdownRawHTMLForm(forms.ModelForm):
    class Meta:
        model = RawHTML
        widgets = {
            'body': MarkdownWidget(),
        }
        exclude = ('display_type',)

RawHTMLForm = MarkdownRawHTMLForm
