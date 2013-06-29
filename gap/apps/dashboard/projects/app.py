from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from apps.dashboard.projects import views

class ProjectDashboardApplication(Application):
    project_list = views.ProjectListView
    project_detail = views.ProjectDetailView
    line_detail = views.ProjectLineItemDetailView
    line_follow = views.FollowLineView
    line_unfollow = views.UnfollowLineView

    def get_urls(self):
    	urlpatterns = patterns('',
    		url(r'^$', self.project_list.as_view(), name='project-list'),
            url(r'^(?P<pk>\d+)/$', self.project_detail.as_view(), name='project-detail'),
            url(r'^(?P<pk>\d+)/lines/(?P<line_id>\d+)/$', self.line_detail.as_view(), name='project-line-detail'),
            url(r'^(?P<pk>\d+)/lines/(?P<line_id>\d+)/follow/$', self.line_follow.as_view(), name='follow-project-line'),
    		url(r'^(?P<pk>\d+)/lines/(?P<line_id>\d+)/unfollow/$', self.line_unfollow.as_view(), name='unfollow-project-line'),
    	)
    	return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required

application = ProjectDashboardApplication()