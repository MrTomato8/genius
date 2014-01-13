from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from apps.dashboard.jobs import views

class JobDashboardApplication(Application):
    order_list = views.OrderListView
    job_list = views.JobListView
    job_task_list = views.JobTaskListView
    job_create = views.JobCreateView
    job_edit = views.JobUpdateView
    task_create = views.TaskCreateView
    task_list = views.TaskListView
    task_detail = views.TaskDetailView
    task_edit = views.TaskUpdateView
    task_detail_redirect = views.TaskDetailRedirect
    stage_create = views.StageCreateView
    stage_list = views.StageListView
    send_email = views.SendEmail
    task_follow = views.FollowTaskView
    task_unfollow = views.UnfollowTaskView

    line_detail_view = views.LineDetailView

    delete_common_desc = views.DeleteCommonDesc
    # project_detail = views.ProjectDetailView
    # line_detail = views.ProjectLineItemDetailView
    # line_follow = views.FollowLineView
    # line_unfollow = views.UnfollowLineView

    def get_urls(self):
    	urlpatterns = patterns('',
            url(r'^orders/$', self.order_list.as_view(), name='order-list'),
            url(r'^send/$', self.send_email.as_view(), name='email-sender'),
            url(r'^orders/(?P<order_id>\d+)/create/$', self.job_create.as_view(), name='order-job-create'),
            url(r'^$', self.job_list.as_view(), name='job-list'),
            url(r'^create/$', self.job_create.as_view(), name='job-create'),
            
            
            url(r'^(?P<pk>\d+)/tasks/$', self.job_task_list.as_view(), name='job-task-list'),
            url(r'^(?P<pk>\d+)/$', self.job_task_list.as_view(), name='job-detail'),
            url(r'^(?P<pk>\d+)/edit/$', self.job_edit.as_view(), name='job-edit'),

            url(r'^tasks/$', self.task_list.as_view(), name='task-list'),
            url(r'^tasks/create/$', self.task_create.as_view(), name='task-create'),
            url(r'^(?P<job_id>\d+)/tasks/(?P<pk>\d+)/$', self.task_detail.as_view(), name='task-detail'),
            url(r'^(?P<job_id>\d+)/tasks/detail/$', self.task_detail_redirect.as_view(), name='task-detail-first'),
            url(r'^(?P<job_id>\d+)/tasks/(?P<pk>\d+)/edit/$', self.task_edit.as_view(), name='job-task-edit'),

            url(r'^(?P<pk>\d+)/tasks/(?P<task_id>\d+)/follow/$', self.task_follow.as_view(), name='follow-task'),
            url(r'^(?P<pk>\d+)/tasks/(?P<task_id>\d+)/unfollow/$', self.task_unfollow.as_view(), name='unfollow-task'),
            
            url(r'^(?P<job_id>\d+)/tasks/create/$', self.task_create.as_view(), name='job-task-create'),
            url(r'^(?P<job_id>\d+)/stages/create/$', self.stage_create.as_view(), name='job-stage-create'),

            url(r'^stages/create/$', self.stage_create.as_view(), name='stage-create'),
            url(r'^stages/$', self.stage_list.as_view(), name='stage-list'),

    		url(r'^(?P<job_id>\d+)/common-desc/(?P<pk>\d+)/delete/$', self.delete_common_desc.as_view(), name='delete-common-desc'),
    	)
    	return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required

application = JobDashboardApplication()