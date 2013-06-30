# bengfort.auth.views
#
# Author: Benjamin Bengfort <benjamin@bengfort.com>
#
# $ID: views.py [4] benjamin@bengfort.com $

"""
@todo: document
"""

__docformat__ = "restructuredtext en"
__author__    = "Benjamin Bengfort <benjamin@bengfort.com>"

###########################################################################
## Imports
###########################################################################

import urlparse

from django import http
from models import Student
from django.conf import settings
from django.contrib import messages
from django.utils.http import base36_to_int
from django.core.urlresolvers import reverse
from mixins import DispatchProtectionMixin, LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.views.generic import View, FormView, TemplateView, DetailView
from django.contrib.auth import authenticate, REDIRECT_FIELD_NAME, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm, SetPasswordForm

###########################################################################
## User Management Views
###########################################################################

class UserProfileView(LoginRequiredMixin, TemplateView):

    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['student'] = Student.fromUser(self.request.user)
        return context

class TeacherProfileView(DetailView):
    """
    Hacked together detail view for teacher profiles. The teacher.html
    template simply overrides the profile.html template and then empties
    blocks that are not relevent. Teachers itself are determined by the
    `get_object` logic that raises a 404 if the returned instance from the
    super method is not a teacher or a teaching assitant. In the future,
    we'll need a teacher manager to handle this.

    Also note that the url is defined in the main urls.py -- we'll need to
    abstract this better when we allow for both student and teacher
    profiles in a more formal manner.
    """

    model = Student
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = "teacher.html"

    def get_object(self):
        instance = super(TeacherProfileView, self).get_object()
        profile  = instance.profile
        if not (profile.is_teacher or profile.is_tassist):
            raise http.Http404("No teacher with the specified username found.")
        return instance

class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    A web view that allows the User to change their password.
    """

    form_class    = PasswordChangeForm
    template_name = "forms/change-password.html"
    success_url   = "/accounts/profile/"

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        return reverse(self.__class__.__name__)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, u"<strong>Success!</strong> Password changed!")
        return super(ChangePasswordView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ChangePasswordView, self).get_form_kwargs()
        kwargs.update({'user':self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ChangePasswordView, self).get_context_data(**kwargs)
        context['student'] = Student.fromUser(self.request.user)
        return context

###########################################################################
## Authentication Views
###########################################################################

class LoginView(DispatchProtectionMixin, FormView):
    """
    Web based login view that is a class based version of the
    django.contrib.auth.views.login view (a function based views). While
    the function view works, we prefer to use the new generic views in
    order to more easily specify custom form classes and tempaltes.

    @todo: Fix the redirect on login.
    @todo: Refactor away from Librarian specific functionality.

    @ivar form_class: The login form to deliver on GET
    @ivar redirect_field_name: The param name to get from the query string
    @ivar template_name: The template of the login form.
    """

    form_class          = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name       = "forms/login.html"

    def form_valid(self, form):
        """
        User has provided valid credentials, checked by
        C{AuthenticationForm.is_valid()}, therefore login the user and
        return the redirect as specified by C{get_success_url}.

        @return: An HttpResponse, redirecting the user to the success url.
        @rtype: C{HttpResposne}
        """
        login(self.request, form.get_user())
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        If the form is valid, determine the url to redirect the user to:

        This is more complicated than it seems. First, we must determine
        where the user was trying to go when they were forced to login.
        This is introspected via the REQUEST, looking for a urlparam like
        '?next=' However, if success_url is set on the class, it will be
        redirected to no matter what. If niether of these things happen,
        then we check the settings to find out what to do.

        @note: urlparse is used to ensure redirecting to the same host.
        @note: If using a form view, action must be "" to capture the
        query string to get C{self.redirect_field_name}.

        @return: The url to redirect to on login success
        @rtype: C{str}
        """

        if self.success_url:
            redirect_to = self.success_url
        else:
            redirect_to = self.request.REQUEST.get(self.redirect_field_name, '')

        netloc = urlparse.urlparse(redirect_to)[1]

        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        elif netloc and netloc != self.request.get_host():
            # Security check -- don't allow redirection to a different host
            redirect_to = settings.LOGIN_REDIRECT_URL

        return redirect_to

    def set_test_cookie(self):
        """
        A helper method to set a test cookie onto the session for checking
        during the POST to ensure that the same client that requests the
        form is the same client that submits it.
        """
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        """
        A helper method to check the test cookie on the form during a POST
        then deletes the cookie so that no security leak can occur. If
        this isn't too obvious, don't worry- Django has it figured out!

        @return: A boolean concerning the success of the check
        @rtype: C{bool}
        """
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
        """
        Same as ProcessFormView.get() but adds test cookie.


        @return: An HttpResponse with the login form.
        @rtype: C{HttpResponse}
        """
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Same as ProcessFormView.post() but checks the test cookie.

        @return: An HttpResponseRedirect to the success url.
        @rtype: C{HttpResponse}
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            self.check_and_delete_test_cookie()
            return self.form_valid(form)
        else:
            self.set_test_cookie()
            return self.form_invalid(form)

class LogoutView(View):
    """
    Web based logout view that is a class based version of the
    django.contrib.auth.views.logout view (a function based views).

    @note: See LoginView for more details.

    @todo: Fix the redirect on logout.
    @todo: Refactor away from Librarian specific functionality.

    @ivar success_url: The url to redirect to on logout success.
    @ivar redirect_field_name: The param name to get from the query string
    """

    success_url = None
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_success_url(self):
        """
        After logout, determine where to send the user afterwards. this
        isn't as simple as it seems. If success_url is set on the class,
        then you're getting sent their no matter what. Otherwise, see if
        it's in the query string. If not in the query string, attempt to
        reverse the LoginView, Finally, go to the settings to find the
        logout url.

        @note: urlparse is used to ensure no redirect to a different host

        @return: The url to redirect to.
        @rtype: C{str}
        """

        redirect_to = getattr(self, 'success_url', None)

        if not redirect_to:
            redirect_to = self.request.REQUEST.get(self.redirect_field_name, None)
        if not redirect_to:
            redirect_to = reverse(LoginView.__name__)

        # Security Check -- don't allow redirection to a different host
        netloc = urlparse.urlparse(redirect_to)[1]

        if not redirect_to:
            redirect_to = settings.get(LOGOUT_REDIRECT_URL, None)

        elif netloc and netloc != request.get_host():
            redirect_to = settings.LOGOUT_REDIRECT_URL

        return redirect_to

    def dispatch(self, request, *args, **kwargs):
        """
        No matter the method-- we're going to logout the user, therefore
        we override dispatch rather than present a method for the various
        http methods. So, logout the user, and redirect to success url.

        @return: An HttpResponseRedirect to the success url
        @rtype: C{HttpResponse}
        """

        self.request = request
        logout(request)
        return http.HttpResponseRedirect(self.get_success_url())

######################################################################
## Password Reset Views
######################################################################

class PasswordResetView(DispatchProtectionMixin, FormView):
    """
    Web based password reset view that is a class based version of
    django.contrib.auth.views.password_reset. See LoginView for a notes on
    functional views vs. class based views.

    This view is the first in a series of four views. The primary purpose
    of this view is to present a reset form, check if the form is valid,
    and then initiate the password reset process.

    @ivar form_class: The password reset form to render on GET
    @ivar template_name: The name of the template to render on GET
    @ivar token_generator: A function to generate user identifying tokens
    @ivar is_admin_site: Set to False unless part of the CMS admin site
    @ivar email_template: The template of the email to send to the user
    @ivar subject_template: The template of the subject of the email above
    @ivar success_url: The location of the PasswordResetDoneView
    @ivar from_email: The address of whom the email was sent from.
    """

    form_class       = PasswordResetForm
    template_name    = "forms/password-reset.html"
    token_generator  = default_token_generator
    is_admin_site    = False
    email_template   = "emails/password-reset-email.html"
    subject_template = "emails/password-reset-subject.txt"
    success_url      = None
    from_email       = "GeekChic Programming <geekchicpro@gmail.com>"

    def get_success_url(self):
        """
        Determine the success url to redirect the user to on form_valid-
        If it is not explicitly set on the class, reverse the url from the
        class name (as set in urls.py).

        @return: The url to redirect the user to on success.
        @rtype: C{str}
        """
        if self.success_url:
            return self.success_url
        else:
            return reverse(PasswordResetDoneView.__name__)

    def form_valid(self, form):
        """
        If the form is valid, e.g. the email address gets a single user,
        whose password will be reset, then send an email to the user with
        a link to reset their password and redirect to the success url.

        @note: C{form.save} handles the email sending work, with the opts
        constructed at the beginning of this method.

        @return: A response redirect to the success url.
        @rtype: C{HttpResponse}
        """
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template,
            #'subject_template_name': self.subject_template,
            'request': self.request,
        }

        if self.is_admin_site:
            opts = dict(opts, domain_override=self.request.META['HTTP_HOST'])

        form.save(**opts)
        return http.HttpResponseRedirect(self.get_success_url())

class PasswordResetDoneView(TemplateView):
    """
    Web based password reset view that is a class based version of
    django.contrib.auth.views.password_reset_done. See LoginView for notes
    on functional views vs. class based view.

    This view is the second in a series of four views. The primary purpose
    of this view is to indicate to the user that an email with further
    instructions has been sent to the user's email address.

    @ivar template_name: The template that renders this message
    """

    template_name = "password-reset-done.html"

class PasswordResetConfirmView(DispatchProtectionMixin, FormView):
    """
    Web based password reset view that is a class based version of
    django.contrib.auth.views.password_reset_confirm. See LoginView for notes
    on functional views vs. class based views.

    This view is the third in a series of four views. The primary purpose
    of this view is to check a token in the query string to ensure that
    the matching user has initiated a password reset, then present a
    password reset form if valid.

    @ivar uidb36: The base36 User primary key
    @ivar token: The token passed in the query string
    @ivar form_class: The password reset form to display if valid
    @ivar template_name: The name of the template that renders the form
    @ivar token_generator: A function to validate the token generated
    @ivar success_url: The url to redirect to on password change.
    """

    uidb36          = None
    token           = None

    form_class      = SetPasswordForm
    template_name   = "forms/password-change.html"
    token_generator = default_token_generator
    success_url     = None

    def dispatch(self, request, *args, **kwargs):
        """
        No matter the http method, we MUST check the uidb36 and the token
        that was passed in the URL. If these are invalid, then return an
        404 error, we don't want anyone trying to pwn passwords through
        the reset mechanism.

        @return: Dispatch to the HTTP method
        @rtype: C{HttpResponse}
        """
        if not self.check_link(kwargs['uidb36'], kwargs['token']):
            raise http.Http404
        return super(PasswordResetConfirmView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Determine the success url to redirect the user to on form_valid-
        If it is not explicitly set on the class, reverse the url from the
        class name (as set in urls.py).

        @return: The url to redirect the user to on success.
        @rtype: C{str}
        """
        if self.success_url:
            return self.success_url
        else:
            return reverse(PasswordResetCompleteView.__name__)

    def get_form_kwargs(self):
        """
        Aside from the default kwargs passed to the form, lets also pass
        the user object from the C{check_link} method to ensure the form
        can do all it's work.

        @return: A dictionary of keyword arguments for the form.
        @rtype: C{dict}
        """
        kwargs = super(PasswordResetConfirmView, self).get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Generate the context data for rendering the response, but also add
        the validlink boolean that is asserted during C{check_link}.

        @return: A dcitionary containing the context data
        @rtype: C{dict}
        """
        kwargs['validlink'] = self.validlink
        return super(PasswordResetConfirmView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        """
        If the form is valid; e.g. the check_link matches the user to the
        token and the password and confrim_password are the same, save the
        user's password and return the success_url.

        @return: An Http Redirect to the success url.
        @rtype: {HttpResponse}
        """
        form.save()
        return http.HttpResponseRedirect(self.get_success_url())

    def check_link(self, uidb36, token):
        """
        A helper method to determine whether the user as fetched from the
        uidb36 matches the token that was genererated during the password
        reset view. This is extremely important to prevent leaks.

        @return: A boolean indicating the validity of the link.
        @rtype: C{bool}
        """
        assert uidb36 is not None and token is not None
        try:
            uid_int = base36_to_int(uidb36)
            self.user = Student.objects.get(id=uid_int)
        except (ValueError, OverflowError, Student.DoesNotExist):
            self.user = None

        self.validlink = bool(self.user is not None and self.token_generator.check_token(self.user, token))
        return self.validlink

class PasswordResetCompleteView(TemplateView):
    """
    Web based password reset view that is a class based version of
    django.contrib.auth.views.password_reset_complete. See LoginView for
    notes on functional views vs. class based view.

    This view is the fourth in a series of four views. The primary purpose
    of this view is to indicate to the user that they have successfully
    updated thier password!

    @ivar template_name: The template that renders this message
    """

    template_name = "password-reset-complete.html"
