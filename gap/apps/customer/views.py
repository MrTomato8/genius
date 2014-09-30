from oscar.apps.customer.views import AccountSummaryView as CoreAccountSummaryView

from apps.quotes.models import Quote


class AccountSummaryView(CoreAccountSummaryView):
    def get_context_data(self, **kwargs):
        # Add saved quotes to the template context
        ctx = super(CoreAccountSummaryView, self).get_context_data(**kwargs)
        quotes = Quote.objects.filter(user_id = self.request.user.id)
        ctx['saved_quotes'] = kwargs.get('saved_quotes', quotes)
        return ctx

