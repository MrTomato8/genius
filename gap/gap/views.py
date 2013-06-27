from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404, render

# from django.conf import settings
# from django.core import serializers
# from django.http import HttpResponsePermanentRedirect, Http404
# from django.views.generic import ListView, DetailView
from django.db.models import get_model
# from django.utils.translation import ugettext_lazy as _

from oscar.core.loading import get_class
from apps.catalogue.forms import AttributeValueFormSet
# from oscar.apps.catalogue.signals import product_viewed, product_search

Product = get_model('catalogue', 'product')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
AttributeOption = get_model('catalogue', 'AttributeOption')
AttributeOptionGroup = get_model('catalogue', 'AttributeOptionGroup')
AttributeEntityType = get_model('catalogue', 'AttributeEntityType')
ProductReview = get_model('reviews', 'ProductReview')
Category = get_model('catalogue', 'category')
ProductAlert = get_model('customer', 'ProductAlert')
ProductAlertForm = get_class('customer.forms',
                             'ProductAlertForm')


def product_options(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    attribute_values = product.attribute_values.all()

    request.session['options'] = get_options_from_post(request)
    if request.POST:
        fs = AttributeValueFormSet(request.user, product, data=request.POST)
        if fs.is_valid():
            pass
    else:
        fs = AttributeValueFormSet(request.user, product)

    return render(request, 'product_options.html', {
        'formset': fs,
        'product': product,
        'categories':Category.objects.all(),
        'attribute_values':attribute_values,
        'step1_codes': ['papersize', 'orientation'],
        'step2_codes': ['paperweight', 'papertype', 'laminationorencapsulation'],
        })

def get_options_from_post(request):
    opt = []
    for k, option in request.POST.items():
        print k
        print option
        if k[:k.rfind('_')] == 'options':
            opt.append(request.POST.get(k))
        print opt
    return opt

def get_quote(request, id):
    product = get_object_or_404(Product, id=id)
    #prices = product.prices()
    #prices = serializers.serialize('json', product.prices())
    #prices = json.dumps(product.prices())
    #print prices

    return direct_to_template(request, 'get_quote.html',{
        'product': product,
        'categories':2,
        'step':4,
        'prices':{1: 100, 2: 200},
    })
