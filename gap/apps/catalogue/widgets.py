from django import forms
from django.forms.util import flatatt
from django.forms.widgets import SubWidget

from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.html import conditional_escape
from django.utils.encoding import StrAndUnicode, force_unicode


class RadioInput(SubWidget):
    """
    An object used by RadioFieldRenderer that represents a single
    <input type='radio'>.
    """

    def __init__(self, name, value, attrs, choice, index):
        self.name, self.value = name, value
        self.attrs = attrs
        self.choice_value = force_unicode(choice[0])
        try:
            thumb = choice[1].attributeoptionthumbnail
            self.img_label = thumb.img.url
            self.choice_label = force_unicode(choice[1])
        except:
            self.choice_label = force_unicode(choice[1])
            self.img_label = None
        self.index = index

    def __unicode__(self):
        return self.render()

    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        if self.img_label:
            img_label = '<img src="%s"><br>' % self.img_label
        else:
            img_label = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'<label class="grid-1 float-left"%s>%s<br>%s%s</label>' % (label_for, self.tag(), img_label, choice_label))

    def is_checked(self):
        return self.value == self.choice_value

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class CustomRenderer(StrAndUnicode):
    """
    An object used by RadioSelect to enable customization of radio widgets.
    """

    def __init__(self, name, value, attrs, choices):
        self.name, self.value, self.attrs = name, value, attrs
        self.choices = choices

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInput(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioInput(self.name, self.value, self.attrs.copy(), choice, idx)

    def __unicode__(self):
        return self.render()

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return mark_safe(u'\n%s\n' % u'\n'.join([u'%s'
                % force_unicode(w) for w in self]))


class AttributeWidget(forms.RadioSelect):
    renderer = CustomRenderer

    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)
