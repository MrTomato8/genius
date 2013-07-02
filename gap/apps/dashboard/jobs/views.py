from django.db.models.loading import get_model
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, FormView, RedirectView

from .models import Job, Task, Stage
from .forms import JobForm, StageForm, TaskForm


Order = get_model('order', 'Order')

GROUP_SMALL = 'small'
GROUP_LARGE = 'large'
GROUP_EXHIBITION = 'exhibition'


class OrderListView(ListView):
    model = Order
    template_name = 'dashboard/jobs/order_list.html'

    def get_context_data(self, **kwargs):
        ctx = super(OrderListView, self).get_context_data(**kwargs)
        user = self.request.user
        groups = user.groups.values_list('name', flat=True)

        if user.is_superuser:
            ctx['orders'] = self.model.objects.all()
        elif GROUP_LARGE in groups:
            ctx['orders'] = self.model.large.all()
        elif GROUP_SMALL in groups:
            ctx['orders'] = self.model.small.all()
        elif GROUP_EXHIBITION in groups:
            ctx['orders'] = self.model.exhibition.all()

        ctx['staff_breadcrumb'] = self.get_breadcrumb(user, groups)
        return ctx

    def get_breadcrumb(self, user, groups):
        if user.is_superuser:
            return "All Teams"

        if GROUP_LARGE in groups:
            return 'Large Format Digital Team'
        elif GROUP_SMALL in groups:
            return ' Small Format Digital Team'
        elif GROUP_EXHIBITION in groups:
            return 'Exhibition Format Digital Team'
        return ''

class JobListView(ListView):
    model = Job
    template_name = 'dashboard/jobs/job_list.html'


class JobTaskListView(DetailView):
    model = Job
    template_name = 'dashboard/jobs/job_task_list.html'

    def get_context_data(self, **kwargs):
        groups = []
        ctx = super(JobTaskListView, self).get_context_data(**kwargs)
        stages = self.object.stage_set.all()
        ctx['stages'] = stages
        for stage in stages:
            groups.append(self.object.task_set.filter(stage=stage))

        ctx['groups'] = groups
        return ctx

class JobCreateView(CreateView):
    model = Job
    form_class = JobForm
    template_name = 'dashboard/jobs/job_form.html'
    success_url = '/dashboard/jobs/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'order_id' in self.kwargs:
            self.object.order = Order.objects.get(pk=self.kwargs['order_id'])

        self.object.creator = self.request.user
        self.object.save()
        return super(JobCreateView, self).form_valid(form)

    def get_initial(self):
        if 'order_id' not in self.kwargs:
            return {}

        return {
            "order": Order.objects.get(pk=self.kwargs['order_id'])
        }

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'dashboard/jobs/task_form.html'
    success_url = '/dashboard/jobs/tasks/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'job_id' in self.kwargs:
            self.object.job = Job.objects.get(pk=self.kwargs['job_id'])
        self.object.creator = self.request.user
        self.object.save()
        return super(TaskCreateView, self).form_valid(form)

    def get_initial(self):
        if 'job_id' not in self.kwargs:
            return {}

        return {
            "job": Job.objects.get(pk=self.kwargs['job_id'])
        }

class TaskListView(ListView):
    model = Task
    template_name = 'dashboard/jobs/task_list.html'

class TaskDetailView(DetailView):
    model = Task
    template_name = 'dashboard/jobs/task_detail.html'

class TaskDetailRedirect(RedirectView):
    def get_redirect_url(self, **kwargs):
        job = Job.objects.get(pk=self.kwargs['job_id'])
        task = Task.objects.filter(job=job)[0]
        return reverse('task-detail', args=(job.id,task.id))

class StageCreateView(CreateView):
    model = Stage
    form_class = StageForm
    template_name = 'dashboard/jobs/stage_form.html'
    
    def get_success_url(self):
        if 'job_id' in self.kwargs:
            return reverse('job-task-list', args=self.kwargs['job_id'])

        return '/dashboard/jobs/stages/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        if 'job_id' in self.kwargs:
            self.object.jobs.add(Job.objects.get(pk=self.kwargs['job_id']))
      
        return super(StageCreateView, self).form_valid(form)

    def get_initial(self):
        if 'job_id' not in self.kwargs:
            return {}

        return {
            "job": Job.objects.get(pk=self.kwargs['job_id'])
        }

class StageListView(ListView):
    model = Stage
    template_name = 'dashboard/jobs/stage_list.html'