from django.db import models
from django.db.models import get_model


AttributeOption = get_model('catalogue', 'AttributeOption')

class AttributeOptionThumbnail(models.Model):
    img = models.ImageField(upload_to='gallery')
    option = models.OneToOneField(AttributeOption, unique=True, blank=True, null=True)

#    class Meta:
#        app_label = 'catalogue'
