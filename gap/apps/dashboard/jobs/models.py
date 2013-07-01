from django.db import models
from django.db.models.loading import get_model
from django.contrib.auth.models import User

Order = get_model('order', 'Order')

class Job(models.Model):
    order = models.ForeignKey(Order)
    name = models.CharField('Job Name', max_length=250)
    creator = models.ForeignKey(User, related_name="job_creator")


    def __unicode__(self):
        return self.name

class Task(models.Model):
    job = models.ForeignKey(Job)
    creator = models.ForeignKey(User, null=True, blank=True, related_name="task_creator")
    assigned_to = models.ForeignKey(User, null=True, blank=True, related_name="assignet_to")
    description = models.TextField('Description', null=True, blank=True)
    name = models.CharField('Name', max_length=250, null=True, blank=True)
    priority = models.CharField('Priority', max_length=250, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.name
    

class Stage(models.Model):
    jobs = models.ManyToManyField(Job, null=True, blank=True)
    name = models.CharField('Stage Name', max_length=250)
    related_status = models.CharField('Related status', max_length=250)
    is_default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name
    