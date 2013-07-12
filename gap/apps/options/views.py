from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.db import models
from django.core.urlresolvers import reverse
from apps.options.models import OptionPickerGroup
from apps.options import utils
from apps.options.forms import picker_form_factory
from apps.options.forms import QuoteCalcForm, QuoteCustomSizeForm
from django.http import HttpResponseRedirect
from apps.options.session import OptionsSessionMixin
from collections import OrderedDict
from apps.options.calc import OptionsCalculator

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')
Price = models.get_model('pricelist', 'Price')


class PickOptionsView(OptionsSessionMixin, View):
    template_name = 'options/pick.html'

    def get(self, request, *args, **kwargs):
        errors = []

        product = Product.objects.get(pk=kwargs['pk'])

        if not self.session.valid(product):
            self.session.reset_product(product)
            self.session.reset_choices()
            self.session.reset_quantity()
            self.session.reset_custom_size()

        groups = []
        for group in OptionPickerGroup.objects.all():

            pickers = []
            for picker in utils.available_pickers(product, group):

                a_choices = utils.available_choices(product, picker)
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

        self.session.reset_product(product)
        self.session.reset_choices()
        self.session.reset_quantity()
        self.session.reset_custom_size()

        allvalid = True

        groups = []
        # Cache collected OptionChoice objects for quantity field pre-fill
        choices = []

        for group in OptionPickerGroup.objects.all():

            pickers = []
            for picker in utils.available_pickers(product, group):

                a_choices = utils.available_choices(product, picker)
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
                        choices.append(opform.cleaned_data[code])
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
            self.session.reset_quantity(utils.min_order(product, choices))
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

        calc = OptionsCalculator(product)

        dp = utils.discrete_pricing(product)

        custom_size = self.session.get('custom_size', {'width': 0, 'height': 0})

        if dp:
            quantity = None
        else:
            quantity = self.session.get_quantity()

        prices = calc.calculate_cost(
            choices,
            quantity,
            width=custom_size['width'],
            height=custom_size['height'])

        calc_form = QuoteCalcForm(initial={'quantity': quantity})
        custom_size_form = QuoteCustomSizeForm(
            initial=self.session.get('custom_size', {}))

        return render(request, self.template_name, {
            'product': product,
            'choices': choices,
            'params': kwargs,
            'calc_form': calc_form,
            'custom_size_form': custom_size_form,
            'custom_size': utils.custom_size_chosen(choices),
            'prices': OrderedDict(sorted(prices.iteritems(), key=lambda t: t[0])),
            'discrete_pricing': utils.discrete_pricing(product),
            'trade_user': utils.trade_user(request.user),

        })

    def post(self, request, *args, **kwargs):
        errors = []

        product = Product.objects.get(pk=kwargs['pk'])
        calculated_price = 0

        if not self.session.valid(product):
            return HttpResponseRedirect(reverse('options:pick', kwargs=kwargs))

        choices = self.session.get_choices()

        min_order = utils.min_order(product, choices)

        calc = OptionsCalculator(product)

        custom_size_form = QuoteCustomSizeForm(request.POST)
        if custom_size_form.is_valid():
            width = custom_size_form.cleaned_data['width']
            height = custom_size_form.cleaned_data['height']
        else:
            self.session.reset_custom_size()
            width = 0
            height = 0

        self.session.set('custom_size', {'width': width, 'height': height})

        dp = utils.discrete_pricing(product)
        calc_form = QuoteCalcForm(request.POST)

        if calc_form.is_valid():

            self.session.set('quantity', calc_form.cleaned_data['quantity'])

            if dp:
                quantity = None
            else:
                quantity = calc_form.cleaned_data['quantity']
                if quantity < min_order:
                    errors.append('Minimum order quantity for this '
                                  'option set is {0}'.format(min_order))
            prices = calc.calculate_cost(
                choices,
                quantity,
                width=width,
                height=height)

        else:
            prices = utils.available_quantities(product, choices)
            self.session.reset_quantity()

        if len(prices) == 0:
            errors.append('No prices found')

        return render(request, self.template_name, {
            'product': product,
            'choices': choices,
            'params': kwargs,
            'calc_form': calc_form,
            'custom_size_form': custom_size_form,
            'custom_size': utils.custom_size_chosen(choices),
            'prices': OrderedDict(sorted(prices.iteritems(), key=lambda t: t[0])),
            'calculated_price': calculated_price,
            'errors': errors,
            'discrete_pricing': dp,
            'trade_user': utils.trade_user(request.user),

        })


class UploadView(OptionsSessionMixin, TemplateView):
    template_name = 'options/upload.html'
