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

        errors = []

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
                                data={code: session[code]})
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


class QuoteView(TemplateView):
    template_name = 'options/quote.html'
