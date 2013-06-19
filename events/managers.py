from django.db import models
from django.utils.timezone import now

class EventManager(models.Manager):

    def midnight(self):
        return now().replace(hour=0, minute=0, second=0, microsecond=0)

    def upcoming(self):
        midnight = self.midnight()
        query = self.filter(start_date__gte=midnight)
        query = query.order_by('start_date')
        return query

    def previous(self):
        midnight = self.midnight()
        query = self.filter(start_date__lte=midnight)
        query = query.order_by('-start_date')
        return query