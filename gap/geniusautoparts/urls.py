from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from accounts.dashboard.app import application as accounts_app
from accounts.views import AccountBalanceView

#from gap.views import product_options, get_quote
from apps.app import application
#from oscar.app import application

#from apps.dashboard.projects.app import application as projects_app
from apps.dashboard.jobs.app import application as jobs_app

from django.conf.urls.static import static
from apps.options.app import application as options_app
admin.autodiscover()

urlpatterns = patterns('',
    (r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
#    url(r'^admin_tools/', include('admin_tools.urls')),

    url(r'^checkout/paypal/', include('paypal.express.urls')),
    (r'^dashboard/accounts/', include(accounts_app.urls)),

    url(r'^giftcard-balance/', AccountBalanceView.as_view(),
        name="account-balance"),
#    url(r'^product-options/(?P<product_id>\d+)/$', product_options, name='product_options'),
#    url(r'^get-quote/(?P<id>\d+)/$', get_quote, name='get_quote'),
    (r'^pricelist/', include('apps.pricelist.urls')),
    (r'^options/', include(options_app.urls)),
    # url(r'^dashboard/projects/', include(projects_app.urls)),
    url(r'^dashboard/jobs/', include(jobs_app.urls)),

    (r'', include(application.urls))
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#    urlpatterns += patterns('',
#        (r'^static/(?P<path>.*)', 'django.views.static.serve', {'document_root':settings.STATIC_ROOT,'show_indexes': True}),
#        (r'^media/(?P<path>.*)', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT,'show_indexes': True}),
# )
'''
import debug_toolbar
urlpatterns += patterns('',
    url(r'^__debug__/', include(debug_toolbar.urls)),
)
'''