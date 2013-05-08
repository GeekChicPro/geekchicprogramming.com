from base import Notifier, TemplateNotifier, ManagersNotifier, AdminsNotifier, UserNotifier

class NotificationError(Exception):
    """A problem in a generic notifier."""
    pass
