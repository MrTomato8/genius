from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'apps.pricelist.views',
    (r'^import', 'import_pricelist'),
    (r'^list/(?P<slug>\S+)', 'list'),
    (r'^list', 'list'),
)
