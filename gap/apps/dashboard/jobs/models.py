from django.db import models
from django.db.models.loading import get_model
from django.contrib.auth.models import User

from oscar.core.loading import get_class

Order = get_model('order', 'Order')

class Job(models.Model):
    order = models.ForeignKey(Order)
    name = models.CharField('Job Name', max_length=250)
    creator = models.ForeignKey(User, related_name="job_creator", null=True, blank=True)

    # def create_default_sategs(self):
    #     self.stage_set.add(*Stage.objects.filter(is_default=True))

    def __unicode__(self):
        return self.name

class Task(models.Model):
    job = models.ForeignKey(Job)
    creator = models.ForeignKey(User, null=True, blank=True, related_name="task_creator")
    stage = models.ForeignKey('Stage', null=True, blank=True)
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
    description = models.TextField('Description', null=True, blank=True)
    related_status = models.CharField('Related status', max_length=250)
    is_default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

order_placed = get_class('order.signals', 'order_placed')


def receive_order_placed(sender, order, user, **kwargs):
    print('Order is placed')
    stages=Stage.objects.filter(is_default=True)
    job = Job.objects.create(
            order=order,
            name='Default Name',
            creator=user
          )
    job.stage_set.add(*stages)


order_placed.connect(receive_order_placed)