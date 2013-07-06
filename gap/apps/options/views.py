from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.db import models
from django.core.urlresolvers import reverse
from apps.options.models import OptionPickerGroup
from apps.options.utils import available_pickers, available_choices
from apps.options.forms import picker_form_factory
from apps.options.forms import QuoteCalcForm, QuoteCustomSizeForm
from django.http import HttpResponseRedirect
from apps.options.models import OptionChoice
from apps.pricelist.utils import pick_price, MatchingPriceNotFound

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')
Price = models.get_model('pricelist', 'Price')


class PickOptionsView(View):
    template_name = 'options/pick.html'

    def session_clean(self, request, product):
        s = request.session['options_pick'] = {}
        s['product'] = product.pk
        s['choices'] = {}

        return s

    def session_valid(self, request, product):
        try:
            return request.session['options_pick']['product'] == product.pk
        except KeyError:
            return False

    def session_get(self, request, product):
        if not self.session_valid(request, product):
            return self.session_clean(request, product)

        try:
            return request.session['options_pick']
        except KeyError:
            return self.session_clean(request, product)

    def dispatch(self, request, *args, **kwargs):

        errors = []

        product = Product.objects.get(pk=kwargs['pk'])

        if request.method == 'POST':
            session = self.session_clean(request, product)
            allvalid = True
        else:
            session = self.session_get(request, product)
            allvalid = False

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
                            session['choices'][code] = opform.cleaned_data[code].pk

                    elif request.method == 'GET':
                        if session['choices'].get(code, None) is not None:
                            opform = OptionPickerForm(
                                data={code: session['choices'][code]})
                        else:
                            opform = OptionPickerForm()

                    pickers.append(
                        {'picker': picker,
                         'form': opform})

            if pickers:
                groups.append({'group': group, 'pickers': pickers})

        # Check if there are any conflicting selections
        if allvalid:

            # Gather all choices in one set
            allchoices = set()
            for group in groups:
                for picker in group['pickers']:
                    code = picker['picker'].option.code
                    allchoices.add(
                        picker['form'].cleaned_data[code])

            # Walk again to find conflicts
            for group in groups:
                for picker in group['pickers']:

                    code = picker['picker'].option.code
                    choice = picker['form'].cleaned_data[code]

                    picker['form'].choice_errors = []

                    # Filter by intersection
                    conflicts = allchoices & set(choice.conflicts_with.all())

                    if conflicts:
                        allvalid = False

                    for conflict in conflicts:
                        emsg = '{0} is not available with {1}'.format(
                            choice.caption, conflict)
                        picker['form'].choice_errors.append(emsg)

            # If validity was reset there must be conflicting choices
            if not allvalid:
                errors.append('There are some conflicting choices. '
                              'Please review your selections')

        if allvalid:
            return HttpResponseRedirect(reverse('options:quote', kwargs=kwargs))

        return render(request, self.template_name, {
            'product': product,
            'groups': groups,
            'errors': errors,
        })


class QuoteView(View):
    template_name = 'options/quote.html'

    def session_choices(self, request, product):
        choices = []
        session = request.session.get('options_pick', {'product': product,
                                                       'choices': {}})

        for k, pk in session['choices'].items():
            choices.append(OptionChoice.objects.get(pk=pk))

        return choices

    def dispatch(self, request, *args, **kwargs):
        errors = []

        product = Product.objects.get(pk=kwargs['pk'])
        calculated_price = 0

        #TODO: If product is different in session - redirect to pick page


        choices = self.session_choices(request, product)

        #TODO: refactor into pricelist utils
        prices = Price.objects.filter(product=product)

        if prices.values('quantity').distinct().count() > 1:
            discrete_pricing = True
        else:
            discrete_pricing = False

        for choice in choices:
            prices = prices.filter(option_choices=choice)

        quantities = prices.values(
            'quantity', 'rpl_price', 'tpl_price').distinct()

        try:
            custom_size_choice = OptionChoice.objects.get(
                option__code='size', code='custom')
        except OptionChoice.DoesNotExist:
            custom_size_choice = None

        custom_size = custom_size_choice in choices


        #TODO: Detect customer type and present RPL or TPL price
        #TODO: Take discounts, offers, coupons into account, etc
        #      move price calculation outta here

        if request.method == 'POST':
            calc_form = QuoteCalcForm(request.POST)
            if calc_form.is_valid():
                try:
                    pickedprice = pick_price(
                        product, calc_form.cleaned_data['quantity'], choices)

                    #TODO: calc_form.cleaned_data['quantity'] has to be > min-order

                    calculated_price = (calc_form.cleaned_data['quantity'] / pickedprice.quantity) * pickedprice.rpl_price
                except MatchingPriceNotFound:
                    errors.append('Matching price not found!')
            custom_size_form = QuoteCustomSizeForm(request.POST)

        elif request.method == 'GET':
            calc_form = QuoteCalcForm()
            custom_size_form = QuoteCustomSizeForm()

        return render(request, self.template_name, {
            'product': product,
            'choices': choices,
            'params': kwargs,
            'calc_form': calc_form,
            'custom_size_form': custom_size_form,
            'custom_size': custom_size,
            'quantities': quantities,
            'calculated_price': calculated_price,
            'errors': errors,
            'discrete_pricing': discrete_pricing,

        })
