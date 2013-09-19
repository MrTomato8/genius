from django.views.generic import View
from django.db import models, DatabaseError
from django.core.urlresolvers import reverse
from apps.options.models import OptionPickerGroup, ArtworkItem
from apps.options import utils
from apps.options.forms import picker_form_factory
from apps.options.forms import QuoteCalcForm, QuoteCustomSizeForm, QuoteSaveForm, QuoteLoadForm
from django.http import HttpResponseRedirect
from apps.options.session import OptionsSessionMixin
from apps.options.calc import OptionsCalculator, PriceNotAvailable
from apps.options.forms import ArtworkDeleteForm, ArtworkUploadForm
from django.contrib import messages
from oscar.apps.basket.signals import basket_addition
from django.template.response import TemplateResponse
from apps.quotes.models import Quote
import json
from django.conf import settings
from decimal import Decimal

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')
Price = models.get_model('pricelist', 'Price')
Line = models.get_model('basket', 'Line')


class OptionsContextMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.product = Product.objects.get(pk=kwargs['pk'])

        if not self.session.valid(self.product):
            return HttpResponseRedirect(reverse('options:pick', kwargs=kwargs))

        self.choices = self.session.get_choices()

        return super(OptionsContextMixin, self).dispatch(
            request, *args, **kwargs)


class PickOptionsView(OptionsSessionMixin, View):
    template_name = 'options/pick.html'

    def get(self, request, *args, **kwargs):
        errors = []

        product = Product.objects.get(pk=kwargs['pk'])

        if not self.session.valid(product):
            self.session.reset_product(product)
            self.session.reset_choices()
            self.session.reset_quantity()
            self.session.reset_choice_data()

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

        return TemplateResponse(request, self.template_name, {
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
        self.session.reset_choice_data()

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

        return TemplateResponse(request, self.template_name, {
            'product': product,
            'groups': groups,
            'errors': errors,
        })


class QuoteView(OptionsSessionMixin, OptionsContextMixin, View):
    template_name = 'options/quote.html'

    def get(self, request, *args, **kwargs):
        errors = []

        calc = OptionsCalculator(self.product)

        choice_data = self.session.get_choice_data()

        quantity = self.session.get_quantity()

        min_order = utils.min_order(self.product, self.choices)
        min_area = utils.min_area(self.product, self.choices)

        if min_order > quantity:
            errors.append('Minimum order quantity for this '
                          'option set is {0}'.format(min_order))

        if min_area > 0:
            errors.append('Minimum custom size area for this '
                          'option set is {0}'.format(min_area))

        prices = calc.calculate_costs(self.choices, quantity, choice_data)

        calc_form = QuoteCalcForm(data={'quantity': quantity})

        choice_data_custom_size = self.session.get_choice_data_custom_size()
        custom_size_form = QuoteCustomSizeForm(initial=choice_data_custom_size)

        quote_save_form = QuoteSaveForm()

        return TemplateResponse(request, self.template_name, {
            'product': self.product,
            'choices': self.choices,
            'params': kwargs,
            'calc_form': calc_form,
            'custom_size_form': custom_size_form,
            'custom_size': utils.custom_size_chosen(self.choices),
            'prices': prices,
            'trade_user': utils.trade_user(request.user),
            'quote_save_form': quote_save_form,
            'errors': errors,
        })

    def post(self, request, *args, **kwargs):
        errors = []

        min_order = utils.min_order(self.product, self.choices)
        min_area = utils.min_area(self.product, self.choices)

        calc = OptionsCalculator(self.product)

        custom_size_form = QuoteCustomSizeForm(request.POST)
        if custom_size_form.is_valid():
            width = custom_size_form.cleaned_data['width']
            height = custom_size_form.cleaned_data['height']
            if min_area > Decimal(width * height) / 1000000:
                errors.append('Minimum custom size area for this '
                              'option set is {0}'.format(min_area))
            self.session.set_choice_data_custom_size(
                {'width': custom_size_form.cleaned_data['width'],
                 'height': custom_size_form.cleaned_data['height']})
        else:
            self.session.set_choice_data_custom_size({'width': 0, 'height': 0})

        choice_data = self.session.get_choice_data()

        calc_form = QuoteCalcForm(request.POST)
        if calc_form.is_valid():
            self.session.set('quantity', calc_form.cleaned_data['quantity'])

            quantity = calc_form.cleaned_data['quantity']
            if quantity < min_order:
                errors.append('Minimum order quantity for this '
                              'option set is {0}'.format(min_order))

            prices = calc.calculate_costs(self.choices, quantity, choice_data)

            try:
                price, nr_of_units, items_per_pack = prices.get_price_incl_tax(
                    quantity, request.user)
            except PriceNotAvailable:
                quote = {'valid': False}
            else:
                quote = {'valid': True}
                quote['price'] = price
                quote['nr_of_units'] = nr_of_units
                quote['items_per_pack'] = items_per_pack
                quote['quantity'] = quantity

        else:
            prices = calc.calculate_costs(self.choices, None, choice_data)
            quote = {'valid': False}

        if len(prices) == 0:
            errors.append('No prices found')

        quote_save_form = QuoteSaveForm()
        if self.request.is_ajax():
            self.template_name = 'options/partials/quote-content.html'
        return TemplateResponse(request, self.template_name, {
            'product': self.product,
            'choices': self.choices,
            'params': kwargs,
            'calc_form': calc_form,
            'custom_size_form': custom_size_form,
            'custom_size': utils.custom_size_chosen(self.choices),
            'prices': prices,
            'errors': errors,
            'trade_user': utils.trade_user(request.user),
            'quote': quote,
            'choice_data_custom_size': self.session.get_choice_data_custom_size(),
            'quote_save_form': quote_save_form,
        })


class QuoteSaveView(OptionsSessionMixin, OptionsContextMixin, View):
    def post(self, request, *args, **kwargs):
        form = QuoteSaveForm(request.POST)
        if form.is_valid():
            if len(form.cleaned_data['reference']) > 0:
                try:
                    quote = Quote()
                    quote.caption = form.cleaned_data['reference']
                    quote.user = request.user
                    quote.product = self.product
                    quote.quantity = self.session.get_quantity()
                    quote.choice_data = json.dumps(
                        self.session.get_choice_data())
                    quote.save()
                    quote.choices = self.choices
                    quote.save()
                except DatabaseError:
                    msg = 'Error saving reference {0}'.format(quote.caption)
                    messages.add_message(request, messages.ERROR, msg)
                else:
                    msg = 'Saved reference {0}'.format(quote.caption)
                    messages.add_message(request, messages.SUCCESS, msg)

                    quotes = Quote.objects.filter(user=request.user)
                    if quotes.count() > settings.MAX_SAVED_QUOTES:
                        quotes.reverse()[0].delete()

        return HttpResponseRedirect(
            reverse('options:upload',
                    kwargs={'product_slug': kwargs['product_slug'],
                            'pk': kwargs['pk']}))


class QuoteLoadView(OptionsSessionMixin, View):
    def post(self, request, *args, **kwargs):
        product = Product.objects.get(pk=kwargs['pk'])

        form = QuoteLoadForm(request.user, product, request.POST)
        if form.is_valid():
            quote = form.cleaned_data['quote']

            if quote.is_valid():
                self.session.reset_product(quote.product)

                choice_dict = {}
                for choice in quote.choices.all():
                    choice_dict[choice.option.code] = choice.pk
                self.session.reset_choices(choice_dict)

                self.session.reset_quantity(quote.quantity)
                self.session.reset_choice_data(json.loads(quote.choice_data))
            else:
                return HttpResponseRedirect(
                    reverse('options:pick',
                            kwargs={'product_slug': kwargs['product_slug'],
                                    'pk': kwargs['pk']}))

            return HttpResponseRedirect(
                reverse('options:quote',
                        kwargs={'product_slug': kwargs['product_slug'],
                                'pk': kwargs['pk']}))
        else:
            return HttpResponseRedirect(
                reverse('catalogue:detail',
                        kwargs={'product_slug': kwargs['product_slug'],
                                'pk': kwargs['pk']}))


class ArtworkDeleteView(View):
    def post(self, request, *args, **kwargs):
        form = ArtworkDeleteForm(request.POST)
        if form.is_valid():
            ArtworkItem.objects.filter(
                user=request.user, pk=kwargs['file_id']).delete()
        return HttpResponseRedirect(
            reverse('options:upload',
                    kwargs={'product_slug': kwargs['product_slug'],
                            'pk': kwargs['pk']}))


class AddToBasketView(OptionsSessionMixin, OptionsContextMixin, View):
    add_signal = basket_addition

    def post(self, request, *args, **kwargs):

        basket = request.basket
        user = request.user
        quantity = self.session.get_quantity()
        choice_data = self.session.get_choice_data()
        attachments = []
        for file in ArtworkItem.objects.filter(user=user):
            if file.available:
                attachments.append(file)

        basket.add_dynamic_product(self.product, quantity, self.choices,
                                   attachments, choice_data)
        msg = '{0} added successfully'.format(self.product.get_title())
        messages.add_message(request, messages.SUCCESS, msg)

        self.add_signal.send(sender=self, product=self.product, user=user)

        return HttpResponseRedirect(reverse('basket:summary'))


class UploadView(OptionsSessionMixin, OptionsContextMixin, View):
    template_name = 'options/upload.html'

    def get_items(self, user):
        items = []
        files = ArtworkItem.objects.filter(user=user)
        for file in files:
            if file.available:
                items.append({'file': file,
                              'form': ArtworkDeleteForm()})
        return items

    def get(self, request, *args, **kwargs):
        items = self.get_items(request.user)
        uploadform = ArtworkUploadForm()
        return TemplateResponse(request, self.template_name, {
            'product': self.product,
            'choices': self.choices,
            'params': kwargs,
            'items': items,
            'uploadform': uploadform,
            'choice_data_custom_size': self.session.get_choice_data_custom_size(),
        })

    def post(self, request, *args, **kwargs):
        items = self.get_items(request.user)
        item = ArtworkItem()
        item.user = request.user
        uploadform = ArtworkUploadForm(
            request.POST, request.FILES, instance=item)

        if uploadform.is_valid():
            uploadform.save()
            return HttpResponseRedirect(reverse('options:upload', kwargs=kwargs))

        return TemplateResponse(request, self.template_name, {
            'product': self.product,
            'choices': self.choices,
            'params': kwargs,
            'items': items,
            'uploadform': uploadform,
            'choice_data_custom_size': self.session.get_choice_data_custom_size(),
        })
