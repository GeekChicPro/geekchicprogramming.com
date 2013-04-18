from django.conf.urls import patterns, url
from workshop.views import *

urlpatterns = patterns('', 
    url(r'^$', ScheduleView.as_view(), name="schedule"),
    url(r'^syllabus/$', SyllabusView.as_view(), name="syllabus"),
    url(r'^module\-(?P<module>\w+)/(?P<doctype>\w+)/$', ModuleView.as_view(), name="module"),
)
