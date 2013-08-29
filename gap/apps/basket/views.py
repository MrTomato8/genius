from apps.basket.exceptions import ItemsRequiredException
from oscar.apps.basket.views import BasketView as CoreBasketView
from apps.basket.forms import BasketLineForm

class BasketView(CoreBasketView):
    form_class = BasketLineForm
    def formset_valid(self, formset):
        '''
        Only some check
        '''
        # Never thrust user input
        for form in formset:
            line = form.instance
            if line.stockrecord_source == line.PRODUCT_STOCKRECORD:
                if form.cleaned_data['items_required'] is not None:
                    # TODO(): we should return some error text
                    raise ItemsRequiredException('PRODUCT_STOCKRECORD should have items_required == None')
                    
        return super(BasketView, self).formset_valid(formset)
    pass
