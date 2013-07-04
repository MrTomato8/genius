from django.db import models

Option = models.get_model('catalogue', 'Option')

#TODO: move OptionChoice here?


class OptionPickerGroup(models.Model):
    name = models.CharField('Name', max_length=30)
    position = models.PositiveSmallIntegerField(
        'Position', default=0, db_index=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['position']


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
        return 'Present {0} as {1} at {2} in {3}'.format(
            str(self.option), self.widget, str(self.position), str(self.group))

    class Meta:
        ordering = ['group', 'position']




# quotes here?
