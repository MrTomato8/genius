from django.db import models as m

class LineManager (m.Manager):
    def get_query_set(self):
        return super(LineManager, self).get_query_set()\
            .prefetch_related('attributes').prefetch_related('attributes__option')