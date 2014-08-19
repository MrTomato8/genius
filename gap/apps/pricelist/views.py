from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from apps.pricelist.forms import PricelistUploadForm
from django.core.urlresolvers import reverse
from apps.pricelist.utils import import_csv
from apps.pricelist.models import Price
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from oscar.views.decorators import staff_member_required
from .models import CsvRow,CSV
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
import json
import csv
Option = models.get_model('catalogue', 'Option')
ProductClass = models.get_model('catalogue', 'ProductClass')

@staff_member_required
def import_pricelist(request):
    if request.method == 'POST':
        form = PricelistUploadForm(request.POST, request.FILES)
        if form.is_valid():
            report = import_csv(
                request.FILES['csvfile'],
                form.cleaned_data['create_options'],
                form.cleaned_data['create_choices'],
                form.cleaned_data['chirurgical'])
            filename=request.FILES['csvfile'].name
            CSV.objects.create(
                name=filename,
                csv_file=request.FILES['csvfile'])
            if report.skipped_total == 0:
                return HttpResponseRedirect(reverse('apps.pricelist.views.list'))
            else:
                return render(request, 'pricelist/importerrors.html',
                              {'report': report})
    else:
        form = PricelistUploadForm()

    return render(request, 'pricelist/import.html', {
        'form': form,
        'title': 'Pricelist Import from CSV',
    })

class CSVList(ListView):
    model = CSV
    template_name = 'pricelist/categories.html'
    context_object_name = 'files'
    def dispatch(self,*args,**kwargs):
        return super(CSVList, self).dispatch(*args,**kwargs)

class CSVUpdate(UpdateView):
    model = CSV
    template_name = 'pricelist/update.html'
    context_object_name = 'csv'
    def post(self,request, pk,*args,**kwargs):

        if not request.is_ajax():
            return None
        csv_obj=CSV.objects.get(pk=pk)
        csv_file = file(csv_obj.csv_file.path,mode='w')
        try:
            csv_writer=csv.writer(csv_file)
            for row in json.loads(request.POST['data']):
                csv_writer.writerow(row)
        finally:
            csv_file.close()
        csv_file = file(csv_obj.csv_file.path)
        try:
            import_csv(csv_file)
        finally:
            csv_file.close()
        return HttpResponse(mimetype='text',content="ok")

@staff_member_required
def list(request, slug=None):
    if slug is None:
        dikt= {}
        for klass in ProductClass.objects.all().prefetch_related('product_set'):
            dikt[klass.name]=[]
            for product in klass.product_set.all():
                dikt[klass.name].append((product.title,product.slug))
        return render(request, 'pricelist/categories.html', {
            'classes':dikt,
            'title': 'Products',
        })
    if request.method=='POST':
        for key in request.POST:
            csvrow= CsvRow.objects.get(pk=key)
            try:
                csvrow.update_field(quantity_discount=request.POST[key])
            except Exception as e:
                print e
        return HttpResponse('200')
    if request.method=='GET':
        prices_all = Price.objects.filter(quantity=1).filter(~Q(state='inactive')).filter(product__slug=slug).prefetch_related('csv')
        paginator = Paginator(prices_all, 20)

        page = request.GET.get('page')
        try:
            prices = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            prices = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            prices = paginator.page(paginator.num_pages)
        prices = prices_all
        headers = ['Product', 'TPL Price', 'RPL Price', 'Quantity',
                'Minimum Order', 'Minimal Area','quantity-discount']


        table = []
        for price in prices:
            row = []
            row.append(price.product)
            row.append(price.tpl_price)
            row.append(price.rpl_price)
            row.append(price.quantity)
            row.append(price.min_order)
            row.append(price.min_area)
            try:
                row.append(price.csv.quantity_discount)
            except:
                row.append('')
            for option in Option.objects.all():
                choices = []
                for choice in price.option_choices.filter(option=option):
                    choices.append(choice.caption)
                choices = ' , '.join(choices)
                if choices != '':
                    row.append(choices)
                    if option.name not in headers:
                        headers.append(option.name)
            try:
                row.append(price.csv.pk)
            except:
                row.append('')
            table.append(row)

        return render(request, 'pricelist/list.html', {
            'prices': prices,
            'paginator': paginator,
            'page_obj': prices,
            'headers': headers,
            'table': table,
            'title': 'Active Prices',
        })
