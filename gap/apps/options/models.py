from django.db import models

Option = models.get_model('catalogue', 'Option')

#TODO: move OptionChoice here?


class OptionPicker(models.Model):
    THUMBNAIL, DROPDOWN = ('thumbnail', 'dropdown')
    WIDGET_CHOICES = ((THUMBNAIL, 'Radio buttons with thumbnails'),
                      (DROPDOWN, 'Dropdown list'))

    option = models.OneToOneField(Option, related_name='picker')
    position = models.PositiveSmallIntegerField(
        'Position', default=0, db_index=True)
    widget = models.CharField('Widget', max_length=10, choices=WIDGET_CHOICES,
                              default=THUMBNAIL)

    def __unicode__(self):
        return 'Present {0} as {1} at {2}'.format(
            str(self.option), self.widget, str(self.position))


class OptionPickerGroup(models.Model):
    name = models.CharField('Name', max_length=30)
    pickers = models.ManyToManyField(
        OptionPicker, related_name='groups', blank=True,
        verbose_name=u'Option Pickers')
    position = models.PositiveSmallIntegerField(
        'Position', default=0, db_index=True)

    def __unicode__(self):
        return self.name


# quotes here?
