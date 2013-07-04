from django.conf.urls import patterns, url, include

from oscar.core.application import Application
from apps.options import views


class BaseOptionsApplication(Application):
    name = 'options'
    pick_view = views.PickOptionsView
    quote_view = views.QuoteView

    def get_urls(self):
        urlpatterns = super(BaseOptionsApplication, self).get_urls()
        urlpatterns += patterns(
            '', url(r'^pick/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
            self.pick_view.as_view(), name='pick'),
            url(r'^quote/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
            self.quote_view.as_view(), name='quote'))


        return self.post_process_urls(urlpatterns)


class OptionsApplication(BaseOptionsApplication):
    pass


application = OptionsApplication()
