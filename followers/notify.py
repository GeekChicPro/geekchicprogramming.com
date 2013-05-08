import logging
from geekchic.utils.notify import ManagersNotifier, TemplateNotifier

def send_signup(name, email):
    logger = logging.getLogger('geekchic.followers')

    if SignUpNotification(name, email).dispatch():
        logger.info("%s <%s> has signed up for email notifications about GeekChic." % (name, email)) 
    else:
        logger.error("There was a problem signing up %s <%s> for notifications, no email sent." % (name, email))

    if not SignUpManagerNotification(name, email).dispatch():
        logger.error("Managers not notified about %s <%s>!!" % (name, email))

class SignUpNotification(TemplateNotifier):
    
    subject = "Thanks for Subscribing to GeekChic Programming!"

    html_template_name = "emails/signup-email.html"
    text_template_name = "emails/signup-email.txt"

    def __init__(self, name, email):
        self.name = name
        self.email = email
        super(SignUpNotification, self).__init__()

    def get_recipients(self):
        return ["%s <%s>" % (self.name, self.email),]

    def get_context_data(self, **kwargs):
        context = super(SignUpNotification, self).get_context_data(**kwargs)
        context['name']  = self.name
        context['email'] = self.email
        return context

class SignUpManagerNotification(ManagersNotifier):

    subject = "Info: New Subscriber"

    html_template_name = "emails/notify-managers-email.html"
    text_template_name = "emails/notify-managers-email.txt"

    def __init__(self, name, email):
        self.name = name
        self.email = email
        super(SignUpManagerNotification, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(SignUpManagerNotification, self).get_context_data(**kwargs)
        context['name']  = self.name
        context['email'] = self.email
        return context
