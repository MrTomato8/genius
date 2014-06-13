from django import forms
from django_markdown.widgets import MarkdownWidget
from oscar.core.loading import get_classes

RawHTML = get_classes('promotions.models', ['RawHTML', ])[0]


class MarkdownRawHTMLForm(forms.ModelForm):
    class Meta:
        model = RawHTML
        widgets = {
            'body': MarkdownWidget(),
        }
        exclude = ('display_type', 'body')

from oscar.apps.dashboard.promotions.forms import RawHTMLForm
RawHTMLForm = MarkdownRawHTMLForm
