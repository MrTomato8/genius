from django.shortcuts import render
from django.http import HttpResponseRedirect
from apps.pricelist.forms import PricelistUploadForm
from django.core.urlresolvers import reverse
from apps.pricelist.utils import import_csv
from apps.pricelist.models import Price
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from oscar.views.decorators import staff_member_required

Option = models.get_model('catalogue', 'Option')


@staff_member_required
def import_pricelist(request):
    if request.method == 'POST':
        form = PricelistUploadForm(request.POST, request.FILES)

        if form.is_valid():
            report = import_csv(
                request.FILES['csvfile'],
                form.cleaned_data['create_options'],
                form.cleaned_data['create_choices'])

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


@staff_member_required
def list(request):
    prices_all = Price.objects.filter(~Q(state='inactive'))
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

    headers = ['Product', 'TPL Price', 'RPL Price', 'Quantity']
    for option in Option.objects.all():
        headers.append(option.name)

    table = []
    for price in prices:
        row = []
        row.append(price.product)
        row.append(price.tpl_price)
        row.append(price.rpl_price)
        row.append(price.quantity)
        for option in Option.objects.all():
            choices = []
            for choice in price.option_choices.filter(option=option):
                choices.append(choice.caption)
            row.append(','.join(choices))
        table.append(row)

    return render(request, 'pricelist/list.html', {
        'prices': prices,
        'paginator': paginator,
        'page_obj': prices,
        'headers': headers,
        'table': table,
        'title': 'Active Prices',
    })
