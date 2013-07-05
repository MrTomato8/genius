from django.db import models

Option = models.get_model('catalogue', 'Option')


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
