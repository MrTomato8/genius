from django.shortcuts import render
from django.views.generic import View
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


class OptionsSession(object):
    SESSION_KEY = 'options_sessiondata'

    def __init__(self, request):
        self.request = request
        if self.SESSION_KEY not in request.session:
            request.session[self.SESSION_KEY] = {}
        self.session = request.session[self.SESSION_KEY]

    def get(self, key, default=None):
        if key in self.request.session[self.SESSION_KEY]:
            return self.request.session[self.SESSION_KEY][key]

        return default

    def set(self, key, value):
        self.request.session[self.SESSION_KEY][key] = value
        self.request.session.modified = True

    def valid(self, product):
        return self.get('product') == product.pk

    def reset_choices(self, product):
        self.set('product', product.pk)
        self.set('choices', {})

    def get_choices(self):
        choices = []

        for k, pk in self.get('choices', {}).items():
            choices.append(OptionChoice.objects.get(pk=pk))

        return choices


class OptionsSessionMixin(object):

    def dispatch(self, request, *args, **kwargs):

        self.session = OptionsSession(request)
        return super(OptionsSessionMixin, self).dispatch(
            request, *args, **kwargs)


class PickOptionsView(OptionsSessionMixin, View):
    template_name = 'options/pick.html'

    def get(self, request, *args, **kwargs):
        errors = []

        product = Product.objects.get(pk=kwargs['pk'])

        if not self.session.valid(product):
            self.session.reset_choices(product)

        groups = []
        for group in OptionPickerGroup.objects.all():

            pickers = []
            for picker in available_pickers(product, group):

                a_choices = available_choices(product, picker)
                if a_choices:
                    OptionPickerForm = picker_form_factory(product,
                                                           picker,
                                                           a_choices)
                    code = picker.option.code
                    s_choices = self.session.get('choices', {})

                    if s_choices.get(code, None) is not None:
                        opform = OptionPickerForm(
                            data={code: s_choices[code]})
                    else:
                        opform = OptionPickerForm()

                    pickers.append(
                        {'picker': picker,
                         'form': opform})

            if pickers:
                groups.append({'group': group, 'pickers': pickers})

        return render(request, self.template_name, {
            'product': product,
            'groups': groups,
            'errors': errors,
        })

    def post(self, request, *args, **kwargs):
        errors = []

        product = Product.objects.get(pk=kwargs['pk'])

        self.session.reset_choices(product)
        allvalid = True

        groups = []
        for group in OptionPickerGroup.objects.all():

            pickers = []
            for picker in available_pickers(product, group):

                a_choices = available_choices(product, picker)
                if a_choices:
                    OptionPickerForm = picker_form_factory(product,
                                                           picker,
                                                           a_choices)
                    code = picker.option.code
                    s_choices = self.session.get('choices', {})

                    opform = OptionPickerForm(request.POST)
                    allvalid = allvalid and opform.is_valid()
                    if opform.is_valid():
                        s_choices[code] = opform.cleaned_data[code].pk
                        self.session.set('choices', s_choices)
                    else:
                        if opform.data.get(code, None) is None:
                            opform.choice_errors.append(
                                'Please select item')

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
                              'Please review your selections.')

        else:
            errors.append('Please review your selections.')

        if allvalid:
            return HttpResponseRedirect(reverse('options:quote', kwargs=kwargs))

        return render(request, self.template_name, {
            'product': product,
            'groups': groups,
            'errors': errors,
        })


class QuoteView(OptionsSessionMixin, View):
    template_name = 'options/quote.html'

    def get(self, request, *args, **kwargs):

        product = Product.objects.get(pk=kwargs['pk'])

        if not self.session.valid(product):
            return HttpResponseRedirect(reverse('options:pick', kwargs=kwargs))

        choices = self.session.get_choices()

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
            'discrete_pricing': discrete_pricing,

        })

    def post(self, request, *args, **kwargs):
        errors = []

        product = Product.objects.get(pk=kwargs['pk'])
        calculated_price = 0

        if not self.session.valid(product):
            return HttpResponseRedirect(reverse('options:pick', kwargs=kwargs))

        choices = self.session.get_choices()

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
