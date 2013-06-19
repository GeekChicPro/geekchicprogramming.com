from events.models import Workshop
from events.mixins import RelativeEventsMixin
from django.views.generic.dates import DateDetailView
from django.views.generic import ListView, TemplateView

class EventSchedule(TemplateView):

    template_name = "programs.html"

class BootcampSchedule(RelativeEventsMixin, TemplateView):

    template_name = "bootcamps.html"

class FellowshipSchedule(RelativeEventsMixin, TemplateView):

    template_name = "fellowships.html"

class WorkshopSchedule(RelativeEventsMixin, ListView):

    model = Workshop
    event_type = Workshop
    template_name = "workshops.html"
    include_previous = True
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.upcoming()

class WorkshopEventDetail(RelativeEventsMixin, DateDetailView):

    model = Workshop
    slug_field = "slug"
    date_field = "start_date"
    template_name = "workshop-event-detail.html"
    allow_future = True
    year_format = "%Y"
    month_format = "%m"
    day_format = "%d"
    event_type = Workshop