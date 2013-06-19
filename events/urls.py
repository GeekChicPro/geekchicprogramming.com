from events.views import *
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', EventSchedule.as_view(), name=EventSchedule.__name__),
    url(r'^bootcamps/$', BootcampSchedule.as_view(), name=BootcampSchedule.__name__),
    url(r'^fellowships/$', FellowshipSchedule.as_view(), name=FellowshipSchedule.__name__),
    url(r'^workshops/$', WorkshopSchedule.as_view(), name=WorkshopSchedule.__name__),
    url(r'^workshops/(?P<year>\d+)/(?P<month>[-\w]+)/(?P<day>\d+)/(?P<slug>[-\w]+)/$', WorkshopEventDetail.as_view(), name=WorkshopEventDetail.__name__),
)