from django import forms
from django.db.models import get_model
from django.forms.models import modelformset_factory, BaseModelFormSet
# from django.utils.translation import ugettext_lazy as _

from apps.catalogue.widgets import AttributeWidget

ProductAttributeValue = get_model('catalogue', 'productattributevalue')


class AttributeValueForm(forms.ModelForm):

    class Meta:
        model = ProductAttributeValue
        fields = ('value_multi_option', 'id')
        widgets = {
            'value_multi_option': AttributeWidget
        }

    def __init__(self, user, product, *args, **kwargs):
        """ Overrides choices for each attributevalue model.
            Takes options belong self.product only.
        """
        self.user = user
        self.product = product
        instance = kwargs.get('instance')
        try:
            choices = product.attribute_values.get(
                attribute__code=instance.attribute.code
            )
            choices = [(value.id, value) for value in choices.value]
        except:
            choices = ()
        self.base_fields['value_multi_option'].choices = choices
        #self.base_fields['value_multi_option'].widget = AttributeWidget()
        super(AttributeValueForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(AttributeValueForm, self).clean()
        is_available = False
        reason= 'disallowed'
        if not is_available:
            raise forms.ValidationError(reason)
        return cleaned_data


class BaseAttributeValueFormSet(BaseModelFormSet):

    def __init__(self, user, product, *args, **kwargs):
        self.user = user
        self.product = product
        super(BaseAttributeValueFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        return super(BaseAttributeValueFormSet, self)._construct_form(
            i, user=self.user, product=self.product, **kwargs)


AttributeValueFormSet = modelformset_factory(ProductAttributeValue, form=AttributeValueForm,
                                        formset=BaseAttributeValueFormSet, extra=0,
                                        can_delete=True)

