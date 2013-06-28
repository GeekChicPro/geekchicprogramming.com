from apply.views import *
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', FellowshipApplicationView.as_view(), name="apply"),
    url(r'^submitted/$', ApplicationSubmitted.as_view(), name="application_submitted"),
)