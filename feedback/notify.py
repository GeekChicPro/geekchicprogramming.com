import logging
from geekchic.utils.notify import ManagersNotifier, UserNotifier

def _notify(feedback, notifier, success_message, error_message, **kwargs):
    logger    = logging.getLogger('geekchic.correspondence')

    if notifier(feedback, **kwargs).dispatch():
        logger.info(success_message)
    else:
        logger.error(error_message)

def send_feedback(feedback):
    raise NotImplementedError("Feedback mechanism currently not implemented.")