from django.db import models
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _

from oscar.apps.catalogue.abstract_models import AbstractProductAttributeValue, AbstractProductAttribute, AbstractProduct


class Product(AbstractProduct):

    @property
    def is_shipping_required(self):
        return False


class ProductAttributeValue(AbstractProductAttributeValue):
    value_multi_option = models.ManyToManyField(
        'catalogue.AttributeOption', blank=True, null=True,
        related_name='multi_option',
        verbose_name=_("Value Multi Option"))

    class Meta:
        verbose_name = _('Product Attribute Value')
        verbose_name_plural = _('Product Attribute Values')

    def _get_value(self):
        if self.attribute.type == 'multi_option':# and isinstance(new_value, str):
            manager = getattr(self, 'value_%s' % self.attribute.type)
            return manager.all()
        return getattr(self, 'value_%s' % self.attribute.type)

    def _set_value(self, new_value):
        if self.attribute.type == 'option' and isinstance(new_value, str):
            # Need to look up instance of AttributeOption
            new_value = self.attribute.option_group.options.get(
                option=new_value)
        setattr(self, 'value_%s' % self.attribute.type, new_value)

    value = property(_get_value, _set_value)


class ProductAttribute(AbstractProductAttribute):

    TYPE_CHOICES = (
        ("text", _("Text")),
        ("integer", _("Integer")),
        ("boolean", _("True / False")),
        ("float", _("Float")),
        ("richtext", _("Rich Text")),
        ("date", _("Date")),
        ("option", _("Option")),
        ("multi_option", _("Multi Option")),
        ("entity", _("Entity"))
    )
    def __init__(self, *args, **kwargs):

        #import ipdb;ipdb.set_trace()
        super(ProductAttribute, self).__init__(*args, **kwargs)
        self.TYPE_CHOICES = (
            ("text", _("Text")),
            ("integer", _("Integer")),
            ("boolean", _("True / False")),
            ("float", _("Float")),
            ("richtext", _("Rich Text")),
            ("date", _("Date")),
            ("option", _("Option")),
            ("multi_option", _("Multi Option")),
            ("entity", _("Entity"))
        )

    def _validate_multi_option(self, value):
        if isinstance(value, models.query.QuerySet):
            for opt in value:
                if not isinstance(opt, get_model('catalogue', 'AttributeOption')):
                    raise ValidationError(
                        _("Must be an AttributeOption model object instance"))
                if not opt.pk:
                    raise ValidationError(_("AttributeOption has not been saved yet"))
                valid_values = self.option_group.options.values_list('option',
                                                                     flat=True)
                if opt.option not in valid_values:
                    raise ValidationError(
                        _("%(enum)s is not a valid choice for %(attr)s") %
                        {'enum': opt, 'attr': self})

    def get_validator(self):
        DATATYPE_VALIDATORS = {
            'text': self._validate_text,
            'integer': self._validate_int,
            'boolean': self._validate_bool,
            'float': self._validate_float,
            'richtext': self._validate_text,
            'date': self._validate_date,
            'entity': self._validate_entity,
            'option': self._validate_option,
            'multi_option': self._validate_multi_option,
        }

        return DATATYPE_VALIDATORS[self.type]

from oscar.apps.catalogue.models import *
