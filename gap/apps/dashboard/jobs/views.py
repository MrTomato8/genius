from django.db.models.loading import get_model
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect,HttpResponse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, FormView, RedirectView, DeleteView
from django.core.mail import send_mail
from .models import Job, Task, Stage, CommonTaskDescription
from apps.order.models import Order
from .forms import JobForm, StageForm, TaskForm
from oscar.apps.dashboard.orders.views import LineDetailView as LineDetailViewBase

import json
from django.views.generic.base import View

Order = get_model('order', 'Order')
Communication = get_model('custumer', 'CommunicationEventType')
GROUP_SMALL = 'small'
GROUP_LARGE = 'large'
GROUP_EXHIBITION = 'exhibition'

class SendEmail(View):
    def post(self, request):
        post = request.POST
        data = {}
        task = Task.objects.get(pk=post['task'])
        print task
        try:
            communication = Communication.objects.get(name=task.name)
        except:
            data['message']="No email found for task name: %s" % task.name
            data['success']=False
            data = json.dumps(data)
            return HttpResponse(data,mimetype="application/json")
        order=Order.objects.get(pk=order)
        ctx ={
            "order":order,
            'task':task
            }
        email = communication.get_messages(ctx)
        try:
            send_mail(email['subject'], email['html'], order.email, 'orders@geniusautoparts.com')
        except:
            data['message']="emails aren't configured properly"
            data['success']=False
            data = json.dumps(data)
            return HttpResponse(data,mimetype="application/json")
        data['message']="Email sent successfully"
        data['success']=True
        data = json.dumps(data)
        return HttpResponse(data,mimetype="application/json")
        pass

        
#!TODO: is this class usefull?
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
    queryset = Job.objects.all().prefetch_related('order')
    template_name = 'dashboard/jobs/job_list.html'
    def get_queryset(self):
        return self.sort_queryset(super(JobListView, self).get_queryset())
    
    def sort_queryset(self, queryset):
        sort = self.request.GET.get('sort', None)
        allowed_sorts = ['order__number',]
        if sort in allowed_sorts:
            direction = self.request.GET.get('dir', 'desc')
            sort = ('-' if direction == 'desc' else '') + sort
            queryset = queryset.order_by(sort)
        return queryset
    def get_context_data(self, **kwargs):
        ctx = super(JobListView, self).get_context_data(**kwargs)
        user = self.request.user
        groups = user.groups.values_list('name', flat=True)

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


class JobTaskListView(DetailView):
    model = Job
    template_name = 'dashboard/jobs/job_task_list.html'

    def get_context_data(self, **kwargs):
        groups = []
        ctx = super(JobTaskListView, self).get_context_data(**kwargs)
        stages = self.object.stage_set.all()
        dict={}
        for stage in stages:
            stage.completeness=stage.completeness(self.object)
            groups.append(self.object.task_set.filter(stage=stage))
        ctx['stages'] =stages
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
        
class JobUpdateView(UpdateView):
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
        return super(JobUpdateView, self).form_valid(form)

    # def get_initial(self):
    #     if 'order_id' not in self.kwargs:
    #         return {}

    #     return {
    #         "order": Order.objects.get(pk=self.kwargs['order_id'])
    #     }

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'dashboard/jobs/task_form.html'
    success_url = '/dashboard/jobs/tasks/'

    def get_success_url(self):
        if 'job_id' in self.kwargs:
            return reverse('job-task-list', args=[self.kwargs['job_id']])

        return '/dashboard/jobs/tasks/'

    def get_context_data(self, **kwargs):
        ctx = super(TaskCreateView, self).get_context_data(**kwargs)
        ctx['common_descriptions'] = CommonTaskDescription.objects.filter(user=self.request.user)

        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'job_id' in self.kwargs:
            self.object.job = Job.objects.get(pk=self.kwargs['job_id'])

        self.object.creator = self.request.user
        # self.objects.create_default_sategs()
        self.object.save()
        if form.cleaned_data['common_description']:
            CommonTaskDescription.objects.create(description=self.object.description, user=self.request.user)

        return super(TaskCreateView, self).form_valid(form)

    def get_initial(self):
        if 'job_id' not in self.kwargs:
            return {}

        return {
            "job": Job.objects.get(pk=self.kwargs['job_id'])
        }

class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'dashboard/jobs/task_form.html'

    def get_success_url(self):
        if 'job_id' in self.kwargs:
            return reverse('job-task-list', args=[self.object.job.id])

        return '/dashboard/jobs/tasks/'

    def get_context_data(self, **kwargs):
        ctx = super(TaskUpdateView, self).get_context_data(**kwargs)
        ctx['common_descriptions'] = CommonTaskDescription.objects.filter(user=self.request.user)

        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)

        self.object.creator = self.request.user
        self.object.save()
        if form.cleaned_data['common_description']:
            CommonTaskDescription.objects.create(description=self.object.description, user=self.request.user)

        return super(TaskUpdateView, self).form_valid(form)

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

    def get_context_data(self, **kwargs):
        ctx = super(TaskDetailView, self).get_context_data(**kwargs)
        job = self.object.job
        job_tasks = list(job.task_set.all())
        task_index = job_tasks.index(self.object)
        ctx['job'] = job
        ctx['followers'] = self.object.followers.all()
        
        # using try here will not work, list supports negative index
        if task_index > 0:
            ctx['prev'] = job_tasks[task_index-1] 

        try:
            ctx['next'] = job_tasks[task_index+1]
        except:
            pass
        
        return ctx


class TaskDetailRedirect(RedirectView):
    def get_redirect_url(self, **kwargs):
        job = Job.objects.get(pk=self.kwargs['job_id'])
        try:
            task = Task.objects.filter(job=job)[0]
        except Exception, e:
            messages.error(self.request, 'You have to create a task first!')
            return reverse('job-task-list', args=(job.id,))
        
        return reverse('task-detail', args=(job.id, task.id))

class NextRedirect(RedirectView):
    def get_redirect_url(self, **kwargs):
        job = Job.objects.get(pk=self.kwargs['job_id'])
        task = Task.objects.get(pk=self.kwargs['task_id'])
        return reverse('task-detail', args=(job.id,task.id))

class PreviousRedirect(RedirectView):
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


class FollowTaskView(DetailView):
    model = Job
    success_message = "You are following this task"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task = self.object.task_set.get(id=self.kwargs['task_id'])
        task.followers.add(request.user)
        messages.success(request, self.success_message)
        return HttpResponseRedirect(reverse('task-detail', kwargs={'pk': task.id, 'job_id': self.object.id}))



class UnfollowTaskView(DetailView):
    model = Job
    success_message = " Unfollowed this task successfully"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task = self.object.task_set.get(id=self.kwargs['task_id'])
        task.followers.remove(request.user)
        messages.success(request, self.success_message)
        return HttpResponseRedirect(reverse('task-detail', kwargs={'pk': task.id, 'job_id': self.object.id}))



class DeleteCommonDesc(DeleteView):
    model = CommonTaskDescription

    def get_success_url(self):
        if 'job_id' in self.kwargs:
            return reverse('job-task-create', args=[self.kwargs['job_id']])

        return '/dashboard/jobs/tasks/'

class LineDetailView(LineDetailViewBase):
    def get_context_data(self, **kwargs):
        import ipdb; ipdb.set_trace()
        ctx = super(LineDetailView, self).get_context_data(**kwargs)
        ctx['item'] = self.object
        ctx['quantity'] = self.object.quantity
        return ctx
