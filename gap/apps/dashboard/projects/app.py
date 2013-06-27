from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application

from apps.dashboard.projects import views

class ProjectDashboardApplication(Application):
    project_list = views.ProjectListView
    project_detail = views.ProjectDetailView

    def get_urls(self):
    	urlpatterns = patterns('',
    		url(r'^$', self.project_list.as_view(), name='project-list'),
    		url(r'^(?P<pk>\d+)$', self.project_detail.as_view(), name='project-detail'),
    	)
    	return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required

application = ProjectDashboardApplication()