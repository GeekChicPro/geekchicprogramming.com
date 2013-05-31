import logging

from auth.models import Student
from geekchic.utils.notify import TemplateNotifier

def send_registration(user, password=None):
    logger = logging.getLogger('geekchic.registration')

    if not isinstance(user, Student):
        user = Student.fromUser(user)

    if RegistrationNotification(user, password).dispatch():
        logger.info("%s has registered as %s" % (user.full_email, user.username))
        return True
    else:
        logger.error("Problem sending password notification to %s" % user.full_email)
        return False

class RegistrationNotification(TemplateNotifier):
    
    subject = "GeekChic: Registration for Workshop Materials"

    html_template_name = "emails/registration-notification.html"
    text_template_name = "emails/registration-notification.txt"

    def __init__(self, user, password=None):
        self.user = user
        self.password = password
        super(RegistrationNotification, self).__init__()

    def get_recipients(self):
        return ["%s" % self.user.full_email]

    def get_context_data(self, **kwargs):
        context = super(RegistrationNotification, self).get_context_data(**kwargs)
        context['user'] = self.user
        context['password'] = self.password
        return context
