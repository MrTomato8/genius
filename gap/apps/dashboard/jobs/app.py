from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from apps.dashboard.jobs import views

class JobDashboardApplication(Application):
    job_list = views.JobListView
    order_list = views.OrderListView
    job_create = views.JobCreateView
    task_create = views.TaskCreateView
    task_list = views.TaskListView
    stage_create = views.StageCreateView
    stage_list = views.StageListView
    # project_detail = views.ProjectDetailView
    # line_detail = views.ProjectLineItemDetailView
    # line_follow = views.FollowLineView
    # line_unfollow = views.UnfollowLineView

    def get_urls(self):
    	urlpatterns = patterns('',
            url(r'^$', self.job_list.as_view(), name='job-list'),
            url(r'^orders/$', self.order_list.as_view(), name='order-list'),
            url(r'^orders/(?P<order_id>\d+)/$', self.job_create.as_view(), name='job-create'),
            url(r'^(?P<job_id>\d+)/tasks/$', self.task_create.as_view(), name='task-create'),
            url(r'^tasks/$', self.task_list.as_view(), name='task-list'),
            url(r'^tasks/create/$', self.task_create.as_view(), name='task-create'),
            url(r'^tasks/(?P<task_id>\d+)/stages/$', self.stage_create.as_view(), name='stage-create'),
            url(r'^stages/create/$', self.stage_create.as_view(), name='stage-create'),
    		url(r'^stages/$', self.stage_list.as_view(), name='stage-list'),
            
    	)
    	return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required

application = JobDashboardApplication()