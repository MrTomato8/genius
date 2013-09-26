from django.db import models as m

class PricelistManager (m.Manager):
    def get_query_set(self):
        return super(PricelistManager, self).get_query_set()\
            .prefetch_related('option_choices')