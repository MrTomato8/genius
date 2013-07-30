from oscar.apps.catalogue import views
from apps.options.forms import QuoteLoadForm
from apps.quotes.models import Quote


class ProductDetailView(views.ProductDetailView):

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['quote_load_form'] = self.get_quote_load_form()

        return ctx

    def get_quote_load_form(self):
        if not self.request.user.is_authenticated():
            return None
        if Quote.objects.filter(
                user=self.request.user, product=self.object).count() > 0:
            return QuoteLoadForm(self.request.user, self.object)
        else:
            return None
