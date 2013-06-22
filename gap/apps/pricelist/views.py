from django.shortcuts import render
from django.http import HttpResponseRedirect
from apps.pricelist.forms import PricelistUploadForm
from django.core.urlresolvers import reverse
from apps.pricelist.utils import import_csv
from apps.pricelist.models import Price
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# TODO:allow staff only
def import_pricelist(request):
    if request.method == 'POST':
        form = PricelistUploadForm(request.POST, request.FILES)
        if form.is_valid():
            import_csv(request.FILES['csvfile'])
            return HttpResponseRedirect(reverse('apps.pricelist.views.list'))
    else:
        form = PricelistUploadForm()

    return render(request, 'pricelist/import.html', {
        'form': form,
        'title': 'Pricelist Import from CSV',
    })

# TODO: this one needs pagination
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
    return render(request, 'pricelist/list.html', {
        'prices': prices,
        'paginator': paginator,
        'page_obj': prices,
        'title': 'Active Prices',
    })
