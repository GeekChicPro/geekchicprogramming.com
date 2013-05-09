from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
from followers.views import AddFollower
from feedback.views import ContactFormView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html"), name="index"),
    url(r'^404/$', TemplateView.as_view(template_name="404.html"), name="404"),
    url(r'^500/$', TemplateView.as_view(template_name="500.html"), name="500"),
    url(r'^legal/$', TemplateView.as_view(template_name="legal.html"), name="legal"),
    url(r'^privacy/$', TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    url(r'^contact-us/$', ContactFormView.as_view(), name="contact"),
    url(r'^signup/$', AddFollower.as_view(), name="email_signup"),
    url(r'^workshops/', include('workshop.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('auth.urls')),
)
