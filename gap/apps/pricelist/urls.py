from django.conf.urls import patterns, url

from apps.pricelist.views import CSVUpdate,CSVList

urlpatterns = patterns(
    'apps.pricelist.views',
    (r'^import', 'import_pricelist'),
    url(r'^list/(?P<pk>\S+)', CSVUpdate.as_view(),name='csvupdate'),
    (r'^list', CSVList.as_view()),
)
