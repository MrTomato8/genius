import simplejson as json
from decimal import Decimal
from smtplib import SMTPException
import cStringIO as StringIO
import ho.pisa as pisa
from cgi import escape

from django.conf import settings
from django.views.generic import View, TemplateView
from django.db import models
from django.core.urlresolvers import reverse, Resolver404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.http import QueryDict
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string, get_template

from oscar.apps.basket.signals import basket_addition
from django.conf import settings

from apps.options.models import OptionPickerGroup, ArtworkItem, OptionChoice
from apps.options import utils
from apps.options.forms import picker_form_factory
from apps.options.forms import QuoteCalcForm, QuoteCustomSizeForm, QuoteSaveForm
from apps.options.session import OptionsSessionMixin
from apps.options.calc import OptionsCalculator
from apps.quotes.models import Quote

Product = models.get_model('catalogue', 'Product')
Option = models.get_model('catalogue', 'Option')
Price = models.get_model('pricelist', 'Price')
Line = models.get_model('basket', 'Line')
Basket = models.get_model('basket', 'Basket')


class OptionPickerMixin(object):
    redirect_url = ''
    template_name = ''
    ajax_template_name = ''
    choices = None
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
        self.kwargs =  kwargs
        self.request = request
        self.GET=self.get_querydict()
        self.get_choices(request)

        return super(OptionPickerMixin,self).dispatch(request,*args,**kwargs)

    def get_choices(self,request):
        if self.choices: return self.choices
        choices = OptionChoice.objects.filter(pk__in =[pk for code,pk in self.GET.items()])
        self.choices = choices
        return self.choices

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
        self.get_product()
        groups = []
        errors = []
        for group in self.get_groups():
            pickers = []
            try:
                pickers_list=group.pickers.all().filter(
                    option__choices__in=self.product.prices.all()[0].options.all()
                ).distinct()
            except:
                pickers_list= []
                messages.add_message(self.request, messages.ERROR, 'Product unavailable')
            # probably we can remove ~5-10 queries optimizing this code
            for picker in pickers_list:
                try:
                    choices_pk=OptionChoice.objects.filter(prices__in=self.product.prices.all())
                except:
                    continue
                choices = picker.option.choices.all().filter(pk__in=choices_pk).select_related('option')
                choices =choices.select_related('option').prefetch_related('conflicts_with')
                OptionPickerForm = picker_form_factory(
                    self.product,
                    picker,
                    choices
                    )

                code = picker.option.pk
                selected = False
                for choice in self.choices:
                    if code==choice.option.pk:
                        selected=True
                        break
                    continue
                if selected:
                    conflict = self.choices & choice.conflicts_with.all()
                    if conflict:
                        sel = OptionChoice.objects.get(pk=code)
                        conf = OptionChoice.objects.get(list(conflict)[0])
                        error = '%s conflict with %s conflicts' %(sel,conf)
                        errors.append(error)
                        OptionPickerForm()
                    else:
                        option_form = OptionPickerForm(
                            {picker.option.code: choice.pk})

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
    def get_tax(self,value):
        return value*settings.TAX

    def get_querydict(self):
        GET = self.request.GET.copy()
        DATA=QueryDict('',mutable=True)
        #Decimal(1000) is needed since the lengths are stored in meters but send in mm
        DATA.__setitem__('width',
            Decimal(GET.pop('width',[0])[0]))
        DATA.__setitem__('height',
            Decimal(GET.pop('height',[0])[0]))
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
        data = self.DATA.dict()
        self.calculator = OptionsCalculator(self.product,self.choices,data)
        return self.calculator

    def get_quantity(self):
        self.quantity = self.quantity or self.DATA.get('quantity',0)
        return self.quantity

    def check_quantity(self):
        calculator = self.get_calculator()
        return calculator.check_quantity()

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
        return calculator.get_discount().discount

    def get_discounts(self):
        self.get_price()
        return self.price.discounts.all()

class LineMixin(QuantityCalcMixin):
    line_pk=None
    line = None

    def get_querydict(self):
        l = self.get_line()
        GET = self.request.GET.copy()
        DATA=QueryDict('',mutable=True)
        DATA.__setitem__('width',Decimal(GET.pop('width',[l.width])[0]))
        DATA.__setitem__('height',Decimal(GET.pop('height',[l.height])[0]))
        DATA.__setitem__('quantity',Decimal(GET.pop('quantity',[l.quantity])[0]))
        DATA.__setitem__('number_of_files',int(GET.pop('number_of_files',[l.number_of_files])[0]))
        GET.pop('csrfmiddlewaretoken',None)
        self.DATA=DATA
        self.GET=GET
        return GET

    def get_product(self):
        if self.product:return self.product
        self.get_line()
        self.product=self.line.product
        return self.product

    def get_line_pk(self):
        return self.line_pk

    def get_line(self):
        if self.line: return self.line
        self.get_line_pk()
        line=Line.objects.all().prefetch_related('choices')
        line=line.select_related('product')
        try:
            self.line=line.get(pk=self.line_pk)
        except Line.DoesNotExist:
            messages.add_message(self.request, messages.ERROR, 'Product not found in basket')
            raise Exception('Line not found')
            raise Resolver404('Line not found')
        return self.line

    def get_choices(self,request):
        if self.choices: return self.choices
        if not self.GET.urlencode():
            self.get_line()
            self.choices=self.line.choices.all()
        else:
            super(LineMixin,self).get_choices(request)

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
        ctx['get']=self.request.GET or \
            '&'.join([choice.option.code+'='+str(choice.pk) for choice in self.choices])\
            +'&'+ self.DATA.urlencode()
        ctx['valid']=calculator.check_quantity()
        ctx['price']=calculator.total_price(self.request.user)
        ctx['tax']=self.get_tax(ctx['price'])
        ctx['total_price']=Decimal(str(round(ctx['price']+ctx['tax'],2)))
        ctx['unit_price']= calculator.price_per_unit(self.request.user)
        ctx['quantity']=self.get_quantity()
        return ctx

    def get(self,*args,**kwargs):
        if self.request.is_ajax():
            calculator = self.get_calculator()
            self.get_quantity()
            action=reverse('options:add-to-basket',kwargs={
                'pk': self.product.pk,
                'product_slug': self.product.slug
                })
            action+="?"
            action+=self.request.GET.urlencode()
            ctx={}
            ctx['price']=calculator.total_price(self.request.user)
            ctx['tax']=self.get_tax(ctx['price'])
            ctx['total_price']=ctx['price']+ctx['tax']
            ctx['unit_price']= calculator.price_per_unit(self.request.user)
            ctx['quantity']=self.get_quantity()
            ctx['valid']=calculator.check_quantity()
            ctx['get']=self.request.GET
            ctx['action']=action
            return HttpResponse(json.dumps(ctx),content_type='text/json')
        return super(QuoteView,self).get(*args,**kwargs)

class AddToBasketView(QuantityCalcMixin, View):
    add_signal = basket_addition

    def post(self, request, *args, **kwargs):
        basket = request.basket
        if not request.basket.pk:basket.save()
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



class LineEditView(LineMixin,QuoteView, TemplateView):
    template_name = 'options/pick.html'
    def get_line_pk(self):
        if self.line_pk:return self.line_pk
        self.line_pk=self.kwargs['line_id']
        return self.line_pk
    def post(self, request, *args, **kwargs):
        self.get_line()
        self.get_choices()
        self.line.choices=self.choices
        self.line.width=self.DATA['width']
        self.line.height=self.data['height']
        self.line.quantity==self.data['quantity']
        self.line.save()


# files upload is yet to develop
class UploadView(View):
    pass
'''
    when should a file been uploaded?
    I think that after AddToBasket the site should open a modal popUp
    so that one can upload the files and or edit them.
    The Line is already created and does contain all the data about itself
    we do not need any get params at this point
'''


class ArtworkDeleteView(View):
    pass


class QuoteEmailView(View):

    def get(self, request, *args, **kwargs):

        data = {}
        if 'quote_id' in request.GET:
            quote = Quote.objects.get(id=request.GET['quote_id'])
            is_new = False
        else:
            quote, is_new = Quote.get_or_create(request.user.id)

        if quote:
            c = Context({'quote': quote})

            subject = render_to_string(
                'options/emails/commtype_your_quote_subject.txt', c)
            text_content = render_to_string(
                'options/emails/commtype_your_quote_body.txt', c)
            html_content = render_to_string(
                'options/emails/commtype_your_quote_body.html', c)

            email = EmailMultiAlternatives(subject, text_content, to=[request.user.email])
            email.attach_alternative(html_content, "text/html")

            try:
                email.send()
            except SMTPException:
                data['message'] = "Error occured during e-mail sending"
                data['success'] = False

                return HttpResponse(json.dumps(data), mimetype="application/json")

            data['message'] = "Email sent successfully"
            data['success'] = True
        else:
            data['message'] = "Error occured."
            data['success'] = False

        return HttpResponse(json.dumps(data), mimetype="application/json")


class QuoteSaveView(View):

    def get(self, request, *args, **kwargs):
        data = {}

        quote, is_new = Quote.get_or_create(request.user.id)

        if quote:
            if is_new:
                data['message'] = "Your quote is successfully saved."
                data['success'] = True
            else:
                data['message'] = "This quote is already saved."
                data['success'] = False
        else:
            data['message'] = "Error occured."
            data['success'] = False

        return HttpResponse(json.dumps(data), mimetype="application/json")


class QuotePrintView(View):

    def get(self, request, *args, **kwargs):

        quote, is_new = Quote.get_or_create(request.user.id)
        if quote:
            return self.render_to_pdf('quotes/quote_pdf.html', {
                'pagesize': 'A4',
                'quote': quote,
            })
        else:
            data = {}
            data['message'] = "Error occured."
            data['success'] = False

            return HttpResponse(json.dumps(data), mimetype="application/json")

    def render_to_pdf(self, template_src, context_dict):

        quote_id = str(context_dict['quote'].reference_number)
        template = get_template(template_src)
        context = Context(context_dict)
        html = template.render(context)
        result = StringIO.StringIO()

        pdf = pisa.pisaDocument(
            StringIO.StringIO(html.encode("ISO-8859-1")), result)

        if not pdf.err:
            response = HttpResponse(
                result.getvalue(), mimetype='application/pdf')
            response['Content-Disposition'] = 'attachment; filename={0}'.format("quote_" + quote_id  + ".pdf")

            return response

        return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


class QuoteBespokeView(View):

    def post(self, request, *args, **kwargs):

        data = {}

        if self.is_valid(request):

            post_data = {
                'name': request.POST['quote-name'],
                'email': request.POST['quote-email'],
                'phone': request.POST['quote-phone'],
                'text': request.POST['quote-text']
            }

            c = Context(post_data)

            subject = render_to_string(
                'options/emails/commtype_bespoke_quote_subject.txt', c)
            text_content = render_to_string(
                'options/emails/commtype_bespoke_quote_body.txt', c)
            html_content = render_to_string(
                'options/emails/commtype_bespoke_quote_body.html', c)

            email = EmailMultiAlternatives(
                subject, text_content, to=[settings.ADMINS[0][1]])
            email.attach_alternative(html_content, "text/html")

            try:
                email.send()
            except SMTPException:
                data['message'] = "Error occured during e-mail sending."
                data['success'] = False
            else:
                data['message'] = "Thank you for your enquiry. We'll contact you soon."
                data['success'] = True
        else:
            data['message'] = "Incorrect data."
            data['success'] = False

        return HttpResponse(json.dumps(data), mimetype="application/json")

    def is_valid(self, request):

        if 'quote-name' not in request.POST \
            or 'quote-email' not in request.POST \
            or 'quote-phone' not in request.POST \
            or 'quote-text' not in request.POST:
            return False

        if len(request.POST['quote-text']) <= 0:
            return False

        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(request.POST['quote-email'])
        except ValidationError:
            return False

        return True


class QuoteRemoveView(View):

    def get(self, request, *args, **kwargs):
        try:
            quote = Quote.objects.get(pk=kwargs['pk'])
            quote.delete()
        except Quote.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'Product not found in basket')

        return HttpResponseRedirect(reverse('customer:summary'))


class QuoteLoadView(OptionsSessionMixin, View):
    pass


class QuoteOrderView(View):
    def get(self, request, *args, **kwargs):

        # basket = request.basket

        # if not request.basket.pk:
        #     basket.save()

        # quote = Quote.objects.get(pk=kwargs['pk'])

        # user = request.user
        # # quantity = self.get_quantity()
        # # choices = self.choices
        # # width = self.DATA['width']
        # # height = self.DATA['height']
        # # attachments = []
        # # if user.is_authenticated():
        # #     for file in ArtworkItem.objects.filter(user=user):
        # #         if file.available:
        # #             attachments.append(file)

        # basket.add_product(
        #     product=self.get_product(),
        #     quantity=quantity,
        #     choices=choices,
        #     height=height,
        #     width=width,
        #     attachments=attachments)

        # self.add_signal.send(sender=self, product=self.product, user=user)

        return HttpResponseRedirect(request.REQUEST.get('next', reverse('basket:summary')))


class QuoteEmailPreviewView(View):
    def get(self, request, *args, **kwargs):
        quote, is_new = Quote.get_or_create(request.user.id)
        c = Context({'quote': quote})
        t = get_template('quotes/quote_email.html')
        return HttpResponse(t.render(c))
