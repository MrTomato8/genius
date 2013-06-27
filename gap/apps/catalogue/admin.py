from django.contrib import admin
from django.db.models import get_model

ProductAttribute = get_model('catalogue', 'ProductAttribute')

#admin.site.unregister(ProductAttribute)

class ProductAttributeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"code": ("name", )}

    # Note the use of formfield_for_dbfield instead of formfield_for_choice_field!
    def formfield_for_dbfield(self, db_field, **kwargs):
        #import ipdb;ipdb.set_trace()
        # Add some logic here to base your choices on.
        if db_field.name == 'type':
            kwargs['widget'].choices = (
                ('b', 'bug'),
                ('e', 'enhancement'),
            )
        return super(ProductAttributeAdmin, self).formfield_for_dbfield(db_field, **kwargs)


#admin.site.register(ProductAttribute, ProductAttributeAdmin)
