from oscar.apps.catalogue import views
from apps.options.forms import QuoteLoadForm


class ProductDetailView(views.ProductDetailView):

    def get_context_data(self, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(**kwargs)
        ctx['quote_load_form'] = self.get_quote_load_form()

        return ctx

    def get_quote_load_form(self):
        return QuoteLoadForm(self.request.user, self.object)
