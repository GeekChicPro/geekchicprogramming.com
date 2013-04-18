from django.views.generic import TemplateView

class ScheduleView(TemplateView):
    
    template_name = "schedule.html"

class SyllabusView(TemplateView):

    template_name = "syllabus.html"
