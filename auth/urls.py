from auth.views import *
from django.conf.urls import patterns, url

urlpatterns = patterns('', 
    url(r'login/$', LoginView.as_view(), name=LoginView.__name__),
    url(r'logout/$', LogoutView.as_view(), name=LogoutView.__name__),
    url(r'profile/$', UserProfileView.as_view(), name=UserProfileView.__name__),
    url(r'password/$', ChangePasswordView.as_view(), name=ChangePasswordView.__name__),
    url(r'password/reset/$', PasswordResetView.as_view(), name=PasswordResetView.__name__),
    url(r'password/reset/done/$', PasswordResetDoneView.as_view(), name=PasswordResetDoneView.__name__),
    url(r'password/reset/confirm/(?P<uidb36>\w{1,13})-(?P<token>\w{1,13}-\w{1,20})/$', PasswordResetConfirmView.as_view(), name=PasswordResetConfirmView.__name__),
    url(r'password/reset/complete/$', PasswordResetCompleteView.as_view(), name=PasswordResetCompleteView.__name__),
)
