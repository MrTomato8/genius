from decimal import Decimal
from django.views.generic import View,TemplateView
from django.db import models, DatabaseError
from django.core.urlresolvers import reverse
from apps.options.models import OptionPickerGroup, ArtworkItem, OptionChoice
from apps.options import utils
from apps.options.forms import picker_form_factory
from apps.options.forms import QuoteCalcForm, QuoteCustomSizeForm, QuoteSaveForm, QuoteLoadForm
from django.http import HttpResponseRedirect, HttpResponse
from apps.options.session import OptionsSessionMixin
from apps.options.calc import OptionsCalculator
from apps.options.forms import ArtworkDeleteForm, ArtworkUploadForm
from django.contrib import messages
from oscar.apps.basket.signals import basket_addition
from django.template.response import TemplateResponse
from apps.quotes.models import Quote
import simplejson as json
from django.conf import settings
from django.http import QueryDict
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


class PricesMixin(object):
    def get_prices_context(self, product, choices, quantity, choice_data):
        try:
            calc = OptionsCalculator(product)
            prices = calc.calculate_costs(choices, quantity, choice_data)
        except Exception as e:
            print 'exception'
            raise e
        more_prices = []
        return {
            'prices': prices,
            'more_prices': more_prices,
            'quantity': quantity,
        }


class CustomSizeFormMixin(object):

    product=None

    def get_custom_size_context(self, session, choices):
        choice_data_custom_size = session.get_choice_data_custom_size()
        custom_size_form = QuoteCustomSizeForm(initial=choice_data_custom_size)
        return {
            'custom_size_form': custom_size_form,
            'custom_size': utils.custom_size_chosen(choices),
        }

class OptionPickerMixin(object):
    redirect_url = ''
    template_name =''
    ajax_template_name=''
    choices = []
    groups = None
    product = None
    pickers = {}

    def urlencode(self):
        return self.request.GET.urlencode()

    def get_template_names(self):
        attr = 'template_name'
        if self.request.is_ajax():
            attr= 'ajax_'+attr
        return [getattr(self,attr)]

    def _get_redirect_url(self):
        return self.redirect_url

    def get_redirect_url(self):
        return self._redirect_url() + '?' +self.urlencode()

    def get_querydict(self):
        return self.request.GET.copy()

    def dispatch(self,request,*args,**kwargs):

        self.request = request
        self.GET=self.get_querydict()
        self.get_choices(request)

        return super(OptionPickerMixin,self).dispatch(request,*args,**kwargs)

    def get_choices(self,request):
        choices = OptionChoice.objects.filter(pk__in =[pk for code,pk in self.GET.items()])
        self.choices = choices

    def ajax_request(self):
        return self.ajax_template_name

    def get_context_data(self,**kwargs):
        ctx=super(OptionPickerMixin,self).get_context_data(**kwargs)
        self.load_pickers()
        ctx.update(self.pickers)
        ctx['get']=self.urlencode()
        return ctx

    def get_product(self):
        if self.product: return self.product
        product = Product.objects
        product.prefetch_related('prices')
        product.prefetch_related('prices__options')
        product.prefetch_related('prices__options__option')
        product.prefetch_related('prices__discounts')
        self.product = product.get(pk=self.kwargs['pk'])
        return self.product

    def get_groups(self):
        #Turn it in an iterator if you're doing this once
        if self.groups:return self.groups
        self.get_product()
        groups =OptionPickerGroup.objects.all()
        groups =groups.prefetch_related('pickers')
        groups = groups.select_related('pickers__option')
        groups = groups.prefetch_related('pickers__option__choices')
        groups = groups.prefetch_related('pickers__option__choices__conflicts_with')
        self.groups = groups
        return self.groups

    def load_pickers(self):
        if self.pickers: return bool(self.pickers['errors'])
        codes =[choice.pk for choice in self.choices]
        self.get_product()
        groups = []
        errors = []
        for group in self.get_groups():
            pickers = []
            for picker in group.pickers.all().filter(option__choices__in=self.product.prices.all()[0].options.all()).distinct():
                try:
                    choices_pk=OptionChoice.objects.filter(prices__in=self.product.prices.all())
                except:
                    continue
                choices = picker.option.choices.all().filter(pk__in=choices_pk).prefetch_related('option')

                OptionPickerForm = picker_form_factory(
                    self.product,
                    picker,
                    choices
                    )
                pass

                code = picker.option.pk
                selected = code in codes

                if selected:
                    conflict = self.choices & choices.conflicts_with.all()
                    if conflict:
                        sel = OptionChoice.objects.get(pk=code)
                        conf = OptionChoice.objects.get(list(conflict)[0])
                        error = '%s conflict with %s conflicts' %(sel,conf)
                        errors.append(error)
                        OptionPickerForm()
                    else:
                        option_form = OptionPickerForm(
                            initial={code: code})
                else:
                    option_form = OptionPickerForm()
                    if self.choices:
                        option_form.choice_errors.append('Please select item')
                pickers.append(
                        {'picker': picker,
                         'form': option_form})
            if pickers:
                groups.append({'group': group, 'pickers': pickers})
        self.pickers = {
            'product': self.product,
            'groups': groups,
            'errors': errors,
            'save_url': reverse('options:add-to-basket',
            kwargs={'pk': self.product.pk, 'product_slug': self.product.slug}),
        }

        return bool(errors)

class QuantityCalcMixin(OptionPickerMixin):
    price = None
    quantity = 0
    quantity_form = None
    calculator = None
    DATA = {}
    template_name=''
    quantity_template_name=''

    def get_querydict(self):
        GET = self.request.GET.copy()
        DATA=QueryDict('',mutable=True)
        DATA.__setitem__('width',Decimal(GET.pop('width',[0])[0]))
        DATA.__setitem__('height',Decimal(GET.pop('height',[0])[0]))
        DATA.__setitem__('quantity',Decimal(GET.pop('quantity',[0])[0]))
        DATA.__setitem__('number_of_files',int(GET.pop('number_of_files',[0])[0]))
        GET.pop('csrfmiddlewaretoken',None)
        self.DATA=DATA
        return GET

    def is_custom_size_context(self):
        return utils.custom_size_chosen(self.choices)

    def get_custom_size_context(self):
        if not self.is_custom_size_context():
            return {'custom_size_form':False, 'custom_size':False}
        width = self.DATA.get('width',0)
        height = self.DATA.get('height',0)
        form = QuoteCustomSizeForm(initial={'width':width,'height':height})
        return {'custom_size_form':form, 'custom_size':True}

    def get_calculator(self):
        if self.calculator: return self.calculator
        self.get_product()
        data = self.DATA
        self.calculator = OptionsCalculator(self.product,self.choices,data)
        return self.calculator

    def get_quantity(self):
        self.quantity = self.quantity or self.DATA.get('quantity',0)
        return self.quantity

    def check_quantity(self):
        quantity = self.get_quantity()
        calculator = self.get_calculator()
        return calculator.check_quantity(quantity)

    def get_quantity_form(self):
        if self.quantity_form: return self.quantity_form
        quantity = self.get_quantity()
        self.quantity_form = QuoteCalcForm(data={'quantity': quantity})
        return self.quantity_form

    def get_context_data(self,**kwargs):
        ctx=super(QuantityCalcMixin,self).get_context_data(**kwargs)
        quote_save_form = QuoteSaveForm()
        self.get_quantity_form()

        ctx.update({
            'calc_form': self.quantity_form,
            'quote_save_form': quote_save_form,
            'choices':self.choices
            })
        ctx.update(self.get_custom_size_context())
        return ctx

    def quantity_form_is_valid(self):
        self.get_quantity_form()
        return self.check_quantity() and self.quantity_form.is_valid()

    def get_price(self):
        if self.price: return self.price
        calculator = self.get_calculator()
        self.price = calculator.price
        return self.price

    def get_discount(self):
        calculator = self.get_calculator()
        self.get_quantity()
        self.get_price()
        if not self.quantity_form_is_valid():
            return False
        return calculator.get_discount(self.quantity).discount

    def get_discounts(self):
        self.get_price()
        return self.price.discounts.all()


class PickOptionsView(OptionPickerMixin, TemplateView):
    template_name = 'options/pick.html'

    def _redirect_url(self):
        return reverse('options:quantity',
                kwargs={'pk': self.product.pk, 'product_slug': self.product.slug})

    def get_context_data(self,**kwargs):

        ctx = super(PickOptionsView,self).get_context_data(**kwargs)
        ctx['pick_action']=self.get_redirect_url()
        return ctx

    def get(self, *args,**kwargs):
        pickers_error = self.load_pickers()
        if pickers_error or not self.choices:
            return super(PickOptionsView,self).get(*args,**kwargs)
        return HttpResponseRedirect(self.get_redirect_url())

class QuantityView(QuantityCalcMixin,TemplateView):
    template_name = 'options/pick.html'
    ajax_template_name ='options/partials/quote-content.html'
    def _redirect_url(self):
        return reverse('options:quote',
                kwargs={'pk': self.product.pk, 'product_slug': self.product.slug})

    def get_pick_url(self):
        return reverse('options:pick',
                kwargs={
                    'pk': self.product.pk,
                    'product_slug': self.product.slug})+self.urlencode()

    def get_context_data(self,**kwargs):
        ctx = super(QuantityView,self).get_context_data(**kwargs)
        ctx['prices'] = self.get_discounts()
        ctx['quantity_action'] =self.get_redirect_url()
        return ctx

    def get(self, *args,**kwargs):
        pickers_error = self.load_pickers()
        if pickers_error or not self.choices:
            return HttpResponseRedirect(self.get_pick_url())
        return super(QuantityView,self).get(*args,**kwargs)

class QuoteView(QuantityView, TemplateView):
    template_name = 'options/pick.html'

    def get_quantity_url(self):
        reverse('options:quantity',
                kwargs={
                    'pk': self.product.pk,
                    'product_slug': self.product.slug})+self.urlencode()
    def get_context_data(self,**kwargs):
        ctx=super(QuoteView,self).get_context_data(**kwargs)
        calculator = self.get_calculator()

        ctx['price']=calculator.total_price(self.get_quantity(),self.request.user)
        ctx['price_per_unit']= calculator.price_per_unit(self.get_quantity(),self.request.user)
        ctx['quantity']=self.get_quantity()
        return ctx

    def get(self,*args,**kwargs):
        if self.request.is_ajax():
            calculator = self.get_calculator()
            self.get_quantity()
            ctx={}
            ctx['total_price']=calculator.total_price(self.quantity,self.request.user)
            ctx['unit_price']= calculator.price_per_unit(self.quantity,self.request.user)
            ctx['quantity']=self.get_quantity()
            ctx['valid']=calculator.check_quantity(self.quantity)
            ctx['get']=self.request.GET
            return HttpResponse(json.dumps(ctx),content_type='text/json')
        return super(QuoteView,self).get(*args,**kwargs)

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


class LineEditView(PickOptionsView):
    def get(self, request, *args, **kwargs):
        try:
            line = Line.objects.select_related('product').get(pk=kwargs.get('line_id'))
        except Line.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'Product not found in basket')
            return HttpResponseRedirect(reverse('catalogue:index'))
        product = line.product
        choices, choices_data = line.get_option_choices()
        choice_dict = {}
        for choice in choices:
            choice_dict[choice.option.code] = choice.pk

        self.session.reset_product(product)
        self.session.reset_choices(choice_dict)
        self.session.reset_quantity(line.quantity)
        self.session.reset_choice_data(choices_data)

        context = self.get_prices_context(product, self.session.get_choices(),
                                          line.quantity, self.session.get_choice_data())
        context.update({'line_being_edited': line})
        try:
            return super(LineEditView, self).get(request, *args, context=context, **kwargs)
        finally:
            # Line will be reset in PickOptionsView.get (so when user navigates to product via catalogues,
            # line_id is reset)
            # so we set line_id after PickOptionsView.get is called
            self.session.reset_line(line.pk)


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


class AddToBasketView(QuantityCalcMixin, View):
    add_signal = basket_addition

    def post(self, request, *args, **kwargs):
        basket = request.basket
        user = request.user
        quantity = self.get_quantity()
        choices = self.choices
        width=self.DATA['width']
        height=self.DATA['height']
        attachments = []
        if user.is_authenticated():
            for file in ArtworkItem.objects.filter(user=user):
                if file.available:
                    attachments.append(file)

        basket.add_product(
            product=self.get_product(),
            quantity=quantity,
            choices=choices,
            height=height,
            width=width,
            attachments=attachments)

        self.add_signal.send(sender=self, product=self.product, user=user)

        return HttpResponseRedirect(request.REQUEST.get('next', reverse('basket:summary')))


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

