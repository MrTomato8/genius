from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from oscar.apps.basket.views import BasketView as CoreBasketView

from apps.basket.forms import BasketLineForm
from apps.basket.models import Line


class BasketView(CoreBasketView):
    form_class = BasketLineForm
    pass


class RemoveItemView(View):
    def post(self, request, line_id):
        try:
            line = Line.objects.get(pk=line_id)
            msg = 'Removed "%s" from basket' % line.product_and_options_description()
            line.delete()
            messages.add_message(request, messages.SUCCESS, msg)
        except Line.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'Product not found in basket')
        return HttpResponseRedirect(request.REQUEST.get('next', reverse('basket:summary')))


class ToggleItemLiveView(View):
    def post(self, request, line_id):
        try:
            line = Line.objects.get(pk=line_id)
            line.is_dead = not line.is_dead
            line.save()
            msg = 'Toggled product on'
            if line.is_dead:
                msg = 'Toggled product off'
            messages.add_message(request, messages.SUCCESS, msg)
        except Line.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'Product not found in basket')
        return HttpResponseRedirect(request.REQUEST.get('next', reverse('basket:summary')))
