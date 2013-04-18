from django.conf.urls import patterns, url
from workshop.views import *

urlpatterns = patterns('', 
    url(r'^$', ScheduleView.as_view(), name="schedule"),
)
