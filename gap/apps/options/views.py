from django.views.generic.base import TemplateView
from django.db import models

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')
OptionChoice = models.get_model('pricelist', 'OptionChoice')
Price = models.get_model('pricelist', 'Price')


class PickOptionsView(TemplateView):
    template_name = 'options/pick.html'

    def get_context_data(self, **kwargs):

        context = super(PickOptionsView, self).get_context_data(**kwargs)

        # TODO: fat models
        context['product'] = Product.objects.get(pk=context['params']['pk'])
        context['opts'] = []

        # TODO: check if product has ptions assigned, or productclass has
        # options assigned

        for o in Option.objects.all():
            c = OptionChoice.objects.filter(
                option=o, prices__in=Price.objects.filter(
                    product=context['product'])).distinct()

            context['opts'].append({'option': o, 'choices': c})

        return context
