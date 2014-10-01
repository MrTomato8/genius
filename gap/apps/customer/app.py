from oscar.apps.customer.app import CustomerApplication as CoreCustomerApplication
from apps.customer.views import AccountSummaryView


class CustomerApplication(CoreCustomerApplication):
    summary_view = AccountSummaryView

application = CustomerApplication()
