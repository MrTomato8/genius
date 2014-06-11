from django.core.urlresolvers import reverse
from apps.options import utils
from django.db import models
from apps.options.models import OptionPickerGroup
from apps.options.forms import picker_form_factory
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from apps.options.session import OptionsSessionMixin
from apps.quotes.models import Quote
from oscar.apps.catalogue import views

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')


class ProductDetailView(OptionsSessionMixin, views.ProductDetailView):
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

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['quote_load_form'] = self.get_quote_load_form()

        return ctx

    def get_quote_load_form(self):
        if not self.request.user.is_authenticated():
            return None
        if Quote.objects.filter(
                user=self.request.user, product=self.object).count() > 0:
            return QuoteLoadForm(self.request.user, self.object)
        else:
            return None
