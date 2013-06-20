from django.shortcuts import render
from django.http import HttpResponseRedirect
from apps.pricelist.forms import PricelistUploadForm
from django.core.urlresolvers import reverse
from apps.pricelist.utils import Pricelist

# TODO:allow staff only
def import_pricelist(request):
    if request.method == 'POST':
        form = PricelistUploadForm(request.POST, request.FILES)
        if form.is_valid():
            Pricelist.importcsv(request.FILES['csvfile'])
            return HttpResponseRedirect(reverse('apps.pricelist.views.statistics'))
    else:
        form = PricelistUploadForm()

    return render(request, 'pricelist/import.html', {
        'form': form,
        'title': 'Pricelist Import from CSV',
    })

def statistics(request):
    pass