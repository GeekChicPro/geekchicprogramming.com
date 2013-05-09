import logging
from geekchic.utils.notify import ManagersNotifier

def send_feedback(feedback):
    logger = logging.getLogger('geekchic.followers')
    detail = feedback.user.get_profile().full_email

    if FeedbackNotification(feedback=feedback).dispatch():
        
        logger.info("%s has left feedback, see database for details." % detail)
    else:
        logger.error("Managers not notified about feedback from %s!" % detail)

class FeedbackNotification(ManagersNotifier):
    
    subject = "Info: We've Received feedback"

    html_template_name = "emails/app-feedback-email.html"
    text_template_name = "emails/app-feedback-email.txt"

    def get_context_data(self, **kwargs):
        context = super(FeedbackNotification, self).get_context_data(**kwargs)
        context['feedback'] = self.feedback
        return context
