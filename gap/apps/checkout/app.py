from oscar.apps.checkout import app

from apps.checkout import views


class CheckoutApplication(app.CheckoutApplication):
    # Replace the payment details view with our own
    #payment_details_view = views.PaymentDetailsView
    index_view = views.IndexView
    pass


application = CheckoutApplication()
