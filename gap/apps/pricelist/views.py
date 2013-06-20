from django.shortcuts import render
from django.http import HttpResponseRedirect
from apps.pricelist.forms import PricelistUploadForm
from django.core.urlresolvers import reverse
from apps.pricelist.utils import import_csv
from apps.pricelist.models import Price
from django.db.models import Q

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


def list(request):
    prices = Price.objects.filter(~Q(state='inactive'))
    return render(request, 'pricelist/list.html', {
        'prices': prices,
        'title': 'List',
    })
