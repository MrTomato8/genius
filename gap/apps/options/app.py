from django.conf.urls import patterns, url, include

from oscar.core.application import Application
from apps.options import views
from django.contrib.auth.decorators import login_required


class BaseOptionsApplication(Application):
    name = 'options'
    pick_view = views.PickOptionsView
    quantity_view = views.QuantityView
    quote_view = views.QuoteView
    upload_view = views.UploadView
    artwork_delete_view = views.ArtworkDeleteView
    add_to_basket_view = views.AddToBasketView
    quote_save_view = views.QuoteSaveView
    quote_load_view = views.QuoteLoadView
    quote_email_view = views.QuoteEmailView
    quote_email_preview_view = views.QuoteEmailPreviewView
    quote_print_view = views.QuotePrintView
    quote_bespoke_view = views.QuoteBespokeView
    quote_delete_view = views.QuoteDeleteView
    line_edit_view = views.LineEditView

    def get_urls(self):
        urlpatterns = super(BaseOptionsApplication, self).get_urls()
        urlpatterns += patterns(
            '', url(r'^pick/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                    self.pick_view.as_view(), name='pick'),
                url(r'^quantity/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                    self.quantity_view.as_view(), name='quantity'),
                url(r'^quote/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                    self.quote_view.as_view(), name='quote'),
                url(r'^quote/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/load/$',
                    self.quote_load_view.as_view(), name='quote-load'),
                url(r'^quote/save/$',
                    self.quote_save_view.as_view(), name='quote-save'),
                url(r'^quote/send/$',
                    self.quote_email_view.as_view(), name='quote-email'),
                url(r'^quote/preview/$',
                    self.quote_email_preview_view.as_view(), name='quote-preview'),
                url(r'^quote/print/$',
                    self.quote_print_view.as_view(), name='quote-print'),
                url(r'^quote/bespoke/$',
                    self.quote_bespoke_view.as_view(), name='quote-bespoke'),
                url(r'^quote/(?P<pk>\d+)/delete/$',
                    self.quote_delete_view.as_view(), name='quote-delete'),
                url(r'^upload/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                    self.upload_view.as_view(), name='upload'),
                url(r'^upload/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/delete/(?P<file_id>\d+)$',
                    self.artwork_delete_view.as_view(), name='upload-artwork-delete'),
                url(r'^add/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                    self.add_to_basket_view.as_view(), name='add-to-basket'),
                url(r'^edit/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/(?P<line_id>\d+)/$', self.line_edit_view.as_view(), name='line-edit'),
        )

        return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, pattern):
        if pattern.name.startswith('upload'):
            return login_required
        if pattern.name in ['quote-save', 'quote-email', 'quote-load', 'quote-print']:
            return login_required
        return None


class OptionsApplication(BaseOptionsApplication):
    pass


application = OptionsApplication()
