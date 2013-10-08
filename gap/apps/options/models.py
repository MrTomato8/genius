from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import os
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

Option = models.get_model('catalogue', 'Option')
Product = models.get_model('catalogue', 'Product')
LineAttachment = models.get_model('basket', 'LineAttachment')


class MissingOptionChoiceThumbnail(object):

    def __init__(self, url=None):
        self.url = url if url else settings.MISSING_OPTIONCHOICE_THUMB_URL


class OptionChoice(models.Model):
    code = models.SlugField('Code', max_length=30)

    option = models.ForeignKey(Option, related_name='choices')
    conflicts_with = models.ManyToManyField(
        'self', blank=True, verbose_name=u'Conflicting Choices',
        help_text='Here you can define choice compatibility rules. '
                  'Select option choices which conflict with current choice'
                  '(example: recycled paper cannot have gloss finish, '
                  'so in recycled paper option choice select gloss finish '
                  'as conflicting choice.). Multiple selections are supported')

    caption = models.CharField('Caption', max_length=30, blank=True)
    thumbnail = models.ImageField('Thumbnail', upload_to='options', blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("code__icontains",)
    
    def get_thumbnail(self):
        if self.thumbnail.name:
            return self.thumbnail
        else:
            return MissingOptionChoiceThumbnail()

    def __unicode__(self):
        return ''.join([str(self.option), ': ', self.code])

    def save(self, *args, **kwargs):

        if len(self.caption) == 0:
            self.caption = self.code

        super(OptionChoice, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('option', 'code')
        ordering = ['option']


class OptionPickerGroup(models.Model):
    name = models.CharField('Name', max_length=30)
    position = models.PositiveSmallIntegerField(
        'Position', default=0, db_index=True)

    def __unicode__(self):
        return '{0}. {1}'.format(str(self.position), self.name)

    class Meta:
        ordering = ['position', 'name']


class OptionPicker(models.Model):
    THUMBNAIL, DROPDOWN = ('thumbnail', 'dropdown')
    WIDGET_CHOICES = ((THUMBNAIL, 'Radio buttons with thumbnails'),
                      (DROPDOWN, 'Dropdown list'))

    group = models.ForeignKey(OptionPickerGroup, related_name='pickers',
                              verbose_name=u'Picker Group')

    option = models.OneToOneField(Option, related_name='picker')
    position = models.PositiveSmallIntegerField(
        'Position', default=0, db_index=True)
    widget = models.CharField('Widget', max_length=10, choices=WIDGET_CHOICES,
                              default=THUMBNAIL)

    def __unicode__(self):
        return '{0}. {1} as {2} in {3}'.format(
            str(self.position), str(self.option), self.widget, self.group.name)

    class Meta:
        ordering = ['group', 'position']


class ArtworkItem(models.Model):
    user = models.ForeignKey(User)
    image = models.FileField(upload_to='artwork/%Y/%m/%d')
    uploaded_on = models.DateTimeField(auto_now_add=True)

    @property
    def available(self):
        try:
            self.lines
        except ObjectDoesNotExist:
            return True
        else:
            if self.lines.count() > 0:
                return False
        return True

    @property
    def filename(self):
        return os.path.basename(self.image.name)

    def __unicode__(self):
        return '{0} uploaded on {1}'.format(str(self.user), str(self.uploaded_on))


# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=ArtworkItem)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `ArtworkItem` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=ArtworkItem)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `ArtworkItem` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = ArtworkItem.objects.get(pk=instance.pk).image
    except ArtworkItem.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
