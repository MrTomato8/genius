from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.db import models
from django.core.urlresolvers import reverse
from apps.options.models import OptionPickerGroup
from apps.options.utils import available_pickers, available_choices
from apps.options.forms import picker_form_factory
from django.http import HttpResponseRedirect

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')
OptionChoice = models.get_model('pricelist', 'OptionChoice')
Price = models.get_model('pricelist', 'Price')


class PickOptionsView(View):
    template_name = 'options/pick.html'

    def dispatch(self, request, *args, **kwargs):

        if request.method == 'POST':
            session = request.session['options_choices'] = {}
            allvalid = True
        else:
            session = request.session['options_choices']
            allvalid = False

        product = Product.objects.get(pk=kwargs['pk'])

        groups = []

        for group in OptionPickerGroup.objects.all():

            pickers = []

            for picker in available_pickers(product, group):

                choices = available_choices(product, picker)
                if choices:
                    OptionPickerForm = picker_form_factory(product,
                                                           picker,
                                                           choices)
                    code = picker.option.code

                    if request.method == 'POST':
                        opform = OptionPickerForm(request.POST)
                        allvalid = allvalid and opform.is_valid()
                        if opform.is_valid():
                            session[code] = opform.cleaned_data[code].pk
                    elif request.method == 'GET':

                        if session.get(code, None) is not None:
                            opform = OptionPickerForm(
                                data={code: str(session[code])})
                        else:
                            opform = OptionPickerForm()

                    pickers.append(
                        {'picker': picker,
                         'form': opform})

            if pickers:
                groups.append({'group': group, 'pickers': pickers})

        if allvalid:
            return HttpResponseRedirect(reverse('options:quote', kwargs=kwargs))

        return render(request, self.template_name, {
            'product': product,
            'groups': groups,
        })


class QuoteView(TemplateView):
    template_name = 'options/quote.html'
