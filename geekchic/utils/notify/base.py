import os

from mail import HtmlEmail
from django.conf import settings
from django.utils.encoding import force_unicode
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured

class ContextMixin(object):
    """
    A default context mixin that passes the keyword arguments
    received by get_context_data as the template context.
    """

    def get_context_data(self, **kwargs):
        if 'notifier' not in kwargs:
            kwargs['notifier'] = self
        return kwargs

class Notifier(object):
    """
    Class based email notifier to send more complex messages
    Just subclass this for specific notifications. 

    @note: This class handles HTML emails specifically.

    @todo: Seperate simple text emails into a base class for 
    the Multipart Notifier -- use an email class to generate
    the response to issue the send command on.
    """

    recipients   = None
    subject      = None
    text_content = None
    html_content = None

    def __init__(self, **kwargs):
        """
        Sets the from_email field and any other keyword
        arguments onto the class.
        """
        self.from_email = getattr(settings, 'SERVER_EMAIL')
        for k,v in kwargs.items():
            setattr(self, k, v)

    def get_recipients(self):
        """
        Checks if there is a recipients list and returns
        that. Otherwise, override this method to do more
        with the reciepient list generation.
        """
        if self.recipients is not None:
            return self.recipients
        raise NotImplementedError("Notifier requires a recipients list")

    def get_subject(self):
        """
        Checks if there is a subject and returns it.
        Otherwise, override this method to do more with
        the subject generation.
        """
        if self.subject is not None:
            return self.subject
        raise NotImplementedError("Notifier requires a subject")

    def render_messages(self):
        """
        As of now, simply return static content. Override this
        method in more complex classes to load templates or
        files to return as the content.

        @note: Must provide both HTML and Text content
        """
        if self.text_content and self.html_content:
            return (self.text_content, self.html_content)
        raise NotImplementedError("Multipart message missing either text or html content")

    def dispatch(self, *args, **kwargs):
        """
        Attempts to send the mail, fails gracefully if 
        something bad goes down. Also sets generic
        args and kwargs on the class for use in other
        methods.
        """
        self.args   = args
        self.kwargs = kwargs

        text, html = self.render_messages()

        email = HtmlEmail( subject    = self.get_subject(),
                           from_email = self.from_email,
                           to         = self.get_recipients(),
                           text       = text,
                           html       = html,
                           connection = self.kwargs.get('connection', None) )
        
        return email.send(fail_silently=self.kwargs.get('fail_silently', False))

class TemplateNotifier(ContextMixin, Notifier):
    """
    A view that renders the email response according
    to specified templates and context data.
    """

    html_template_name = None
    text_template_name = None

    def get_template_names(self):
        """
        Returns a list of the template names to be used.
        """

        if self.html_template_name is None or self.text_template_name is None:
            raise ImproperlyConfigured(
                "TemplateMessageMixin requires either a definition of "
                "'html_template_name' and 'text_template_name' or an "
                "implementation of 'get_template_names()'")
        else:
            return (self.text_template_name, self.html_template_name)

    def render_messages(self):
        """
        Renders the messages according to the template values.

        @note: render_messages is expected to return text, html 
        """
        templates = self.get_template_names()
        context   = self.get_context_data(**self.kwargs)
        return (render_to_string(template, context) for template in templates)


class ManagersNotificationMixin(object):
    """
    Serves as class based wrapper for mail_managers.
    """

    def get_recipients(self):
        managers = getattr(settings, 'MANAGERS', None)
        if managers:
            return ["%s <%s>" % manager for manager in managers]
        return None

class AdminsNotificationMixin(object):
    """
    Serves as a class based wrapper for mail_admins.
    """

    def get_recipients(self):
        admins = getattr(settings, 'ADMINS', None)
        if admins:
            return ["%s <%s>" % admin for admin in admins]

class ManagersNotifier(ManagersNotificationMixin, TemplateNotifier):
    """
    TemplateNotifier that sends to managers.
    """
    pass

class AdminsNotifier(AdminsNotificationMixin, TemplateNotifier):
    """
    TemplateNotifier that sends to admins.
    """
    pass

class UserNotificationMixin(object):
    """
    Serves as a class based wrapper for user.send_email
    """

    def get_context_data(self, **kwargs):
        context = super(UserNotificationMixin, self).get_context_data(**kwargs)
        context['user'] = self.get_user()
        return context

    def get_recipients(self):
        user = self.get_user()
        if user.email is None:
            return None
        email = "%s %s <%s>" % (user.first_name, user.last_name, user.email)

        email = email.split()
        for i, part in enumerate(email):
            if part == "":
                del email[i]
        return [' '.join(email),]

    def get_user(self):
        if hasattr(self, 'user'):
            return self.user
        else:
            return self.kwargs.get('user', None)

class UserNotifier(UserNotificationMixin, TemplateNotifier):
    """
    TemplateNotifier that sends to a particular user,
    that is either passed in at init, or in the kwargs.
    """
    pass
