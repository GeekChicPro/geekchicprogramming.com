import logging
from geekchic.utils.notify import ManagersNotifier, UserNotifier

def _notify(application, notifier, success_message, error_message, **kwargs):
    logger    = logging.getLogger('geekchic.correspondence')

    if notifier(application, **kwargs).dispatch():
        logger.info(success_message)
    else:
        logger.error(error_message)

def notify_applicant(application):
    full_name       = application.applicant.profile.full_name
    success_message = "%s has been notified with details about their application" % full_name
    error_message   = "Unable to notify %s with details of their application" % full_name
    notifier        = ApplicationSubmittedNotification

    return _notify(application, notifier, success_message, error_message)

def notify_managers(application):
    full_email      = application.applicant.profile.full_email
    success_message = "Application received from %s, managers notified." % full_email
    error_message   = "Application received from %s, but there was an error notifying managers." % full_email
    notifier        = ApplicationNotification
    return _notify(application, notifier, success_message, error_message)

class ApplicationNotification(ManagersNotifier):

    subject = "Application Received!!"

    html_template_name = "emails/application-notification-email.html"
    text_template_name = "emails/application-notification-email.txt"

    def __init__(self, application, **kwargs):
        self.application = application
        super(ApplicationNotification, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ApplicationNotification, self).get_context_data(**kwargs)
        context['application'] = self.application
        return context

class ApplicationSubmittedNotification(UserNotifier):

    subject = "GeekChic: Thanks for your Application!"

    html_template_name = "emails/application-submitted-email.html"
    text_template_name = "emails/application-submitted-email.txt"

    def __init__(self, application, **kwargs):
        kwargs['user']   = application.applicant
        self.application = application
        super(ApplicationSubmittedNotification, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ApplicationSubmittedNotification, self).get_context_data(**kwargs)
        context['application'] = self.application
        return context