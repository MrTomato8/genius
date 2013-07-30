from django.conf.urls import patterns, url, include

from oscar.core.application import Application
from apps.options import views
from django.contrib.auth.decorators import login_required


class BaseOptionsApplication(Application):
    name = 'options'
    pick_view = views.PickOptionsView
    quote_view = views.QuoteView
    upload_view = views.UploadView
    artwork_delete_view = views.ArtworkDeleteView
    add_to_basket_view = views.AddToBasketView
    quote_save_view = views.QuoteSaveView
    quote_load_view = views.QuoteLoadView

    def get_urls(self):
        urlpatterns = super(BaseOptionsApplication, self).get_urls()
        urlpatterns += patterns(
            '', url(r'^pick/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
            self.pick_view.as_view(), name='pick'),
            url(r'^quote/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
            self.quote_view.as_view(), name='quote'),
            url(r'^quote/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/save/$',
            self.quote_save_view.as_view(), name='quote-save'),
            url(r'^quote/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/load/$',
            self.quote_load_view.as_view(), name='quote-load'),
            url(r'^upload/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
            self.upload_view.as_view(), name='upload'),
            url(r'^upload/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/delete/(?P<file_id>\d+)$',
            self.artwork_delete_view.as_view(), name='upload-artwork-delete'),
            url(r'^add/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
            self.add_to_basket_view.as_view(), name='add-to-basket')
        )

        return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, pattern):
        if pattern.name.startswith('upload'):
            return login_required
        if pattern.name == 'quote-save' or pattern.name == 'quote-load':
            return login_required
        return None


class OptionsApplication(BaseOptionsApplication):
    pass


application = OptionsApplication()
