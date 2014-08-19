from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from oscar.apps.basket.app import BasketApplication as CoreBasketApplication

from apps.basket import views


class BasketApplication(CoreBasketApplication):
    summary_view = views.BasketView
    remove_item_view = views.RemoveItemView
    toggle_item_live_view = views.ToggleItemLiveView

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^$', self.summary_view.as_view(), name='summary'),
            url(r'^add/$', self.add_view.as_view(), name='add'),
            url(r'^lines/(?P<line_id>\d+)/remove/$', self.remove_item_view.as_view(),
                name='items-remove'),
            url(r'^lines/(?P<line_id>\d+)/toggle_live/$', self.toggle_item_live_view.as_view(),
                name='items-toggle-live'),
            url(r'^vouchers/add/$', self.add_voucher_view.as_view(),
                name='vouchers-add'),
            url(r'^vouchers/(?P<pk>\d+)/remove/$',
                self.remove_voucher_view.as_view(), name='vouchers-remove'),
            url(r'^saved/$', login_required(self.saved_view.as_view()),
                name='saved'),
        )
        return self.post_process_urls(urlpatterns)
application = BasketApplication()
