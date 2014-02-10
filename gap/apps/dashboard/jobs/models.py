
from django.db import models
from django.db.models.loading import get_model
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from oscar.core.loading import get_class
from decimal import Decimal as D
from .exceptions import WrongJob, InvalidJobStatus


Order = get_model('order', 'Order')

class Job(models.Model):
    order = models.ForeignKey(Order, null=True, blank=True)
    name = models.CharField('Job Name', max_length=250)
    creator = models.ForeignKey(User, related_name="job_creator", null=True, blank=True)

    status = models.CharField(_("Status"), max_length=100, null=True, blank=True)

    pipeline = getattr(settings, 'OSCAR_JOB_STATUS_PIPELINE', {})
    cascade = getattr(settings,  'OSCAR_JOB_STATUS_CASCADE', {})

    # def create_default_sategs(self):
    #     self.stage_set.add(*Stage.objects.filter(is_default=True))
    def completeness(self):
        total = D(0); number = D(0)
        for task in self.task_set.all():
            total += task.completeness
            number += 1
        if number == D(0):
            return None
        return D(total/number).quantize(D(10)**-2)

    def completeness_percentage(self):
        completeness = self.completeness()
        if completeness is None:
            return None
        return ('%s ' % completeness) +'%'

    def __unicode__(self):
        return self.name

    def available_statuses(self):
        return self.pipeline.get(self.status, ())

    @staticmethod
    def status_type(status):
        TYPE_NEUTRAL = 1
        TYPE_INFO = 2
        TYPE_ACHIEVEMENT = 3
        TYPE_PROBLEM = 4
        types = {
            'pending': TYPE_NEUTRAL,
            'downloaded': TYPE_INFO,
            'on hold': TYPE_PROBLEM,
            'in progress': TYPE_ACHIEVEMENT,
            'waiting collection': TYPE_ACHIEVEMENT,
            'waiting dispatch': TYPE_ACHIEVEMENT,
            'collected': TYPE_ACHIEVEMENT,
            'dispatched': TYPE_ACHIEVEMENT,
        }
        return types[status]

    def progress(self):
        progress = ['pending']
        if self.status == 'pending':
            return progress

        progress.append('downloaded')
        if self.status == 'downloaded':
            return progress

        if self.status == 'on hold':
            progress.append('on hold')
            return progress

        progress.append('in progress')
        if self.status == 'in progress':
            return progress

        if self.status == 'waiting collection':
            progress.append('waiting collection')
            return progress

        if self.status == 'collected':
            progress.append('waiting collection')
            progress.append('collected')
            return progress

        if self.status == 'waiting dispatch':
            progress.append('waiting dispatch')
            return progress

        if self.status == 'dispatched':
            progress.append('waiting dispatch')
            progress.append('dispatched')
            return progress

    def next_statuses(self):
        return self.pipeline[self.status]

    def set_status(self, new_status):
        if new_status == self.status:
            return

        if new_status not in self.available_statuses():
            raise InvalidJobStatus(_("'%(new_status)s' is not a valid status for job %(name)s "
                                       "(current status: '%(status)s')") % {
                                            'new_status': new_status,
                                            'name': self.name,
                                            'status': self.status})
        # import ipdb; ipdb.set_trace()
        self.status = new_status
        if new_status in self.cascade:
            for line in self.lines.all():
                line.status = self.cascade[self.status]
                line.save()
        self.save()
    set_status.alters_data = True

class Task(models.Model):
    followers = models.ManyToManyField(User)
    job = models.ForeignKey(Job)
    creator = models.ForeignKey(User, null=True, blank=True, related_name="task_creator")
    stage = models.ForeignKey('Stage', null=True, blank=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True, related_name="assignet_to")
    description = models.TextField('Description', null=True, blank=True)
    name = models.CharField('Name', max_length=250, null=True, blank=True)
    priority = models.CharField('Priority', max_length=250, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    completeness = models.PositiveSmallIntegerField(default=0)
    
    def save(self,*args,**kwargs):
        if self.completeness >100:
            self.completeness = 100
        super(Task, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name
    

class Stage(models.Model):
    cache={}
    completeness = None
    jobs = models.ManyToManyField(Job, null=True, blank=True)
    name = models.CharField('Stage Name', max_length=250, unique=True)
    description = models.TextField('Description', null=True, blank=True)
    related_status = models.CharField('Related status', max_length=250)
    is_default = models.BooleanField(default=False)
    
    def completeness(self, job):
        if not job in self.jobs.all():
            raise WrongJob, 'job:%s' % job
        tasks = self.job_tasks(job)
        total = D(0); number = D(0)
        for task in tasks:
            total += task.completeness
            number += 1
        if number == D(0).quantize(D(10)**-2):
            return number
        return D(total/number).quantize(D(10)**-2)
        
    
    def job_tasks(self,job):
        return Task.objects.filter(job=job, stage=self)
    
    def __unicode__(self):
        return self.name


class CommonTaskDescription(models.Model):
    description = models.TextField('Description', null=True, blank=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.description[:30]

def receive_order_placed(sender, order, user, **kwargs):
    stages=Stage.objects.filter(is_default=True)
    job = Job.objects.create(
            order=order,
            name=order.number,
            creator=user,
            status='pending',
          )
    job.stage_set.add(*stages)


order_placed = get_class('order.signals', 'order_placed')
order_placed.connect(receive_order_placed)
