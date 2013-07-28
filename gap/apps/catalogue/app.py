from oscar.apps.catalogue import app
from apps.catalogue import views


class CatalogueApplication(app.CatalogueApplication):
    detail_view = views.ProductDetailView


application = CatalogueApplication()
