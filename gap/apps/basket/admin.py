import oscar.apps.basket.admin
from django.db import models
from django.contrib import admin

LineAttachment = models.get_model('basket', 'LineAttachment')
admin.site.register(LineAttachment)
