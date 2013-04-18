from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html"), name="index"),
    url(r'^legal/$', TemplateView.as_view(template_name="legal.html"), name="legal"),
    url(r'^privacy/$', TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    url(r'^workshop/', include('workshop.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
