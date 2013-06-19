from events.models import Event

class RelativeEventsMixin(object):

    event_type = Event
    include_previous = False

    def get_context_data(self, **kwargs):
        context = super(RelativeEventsMixin, self).get_context_data(**kwargs)
        context['event_type'] = self.event_type.__name__

        if self.event_type._meta.abstract:
            return context

        context['upcoming_events'] = self.event_type.objects.upcoming()[0:5]
        if self.include_previous:
            context['previous_events'] = self.event_type.objects.previous()[0:5]
        return context