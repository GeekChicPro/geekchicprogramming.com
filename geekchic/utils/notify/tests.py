"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from ubnd.notify import Notifier, TemplateNotifier, ManagersNotifier, UserNotifier
from django.test import TestCase

class TestNotifier(Notifier):
    
    subject    = "This is a Test"
    recipients = ["Benjamin Bengfort <benjamin@unboundconcepts.com>",]

    text_content = "Testing 123..."
    html_content = "<p>Testing <strong>123</strong>...</p>"

class TestTemplateNotifier(TemplateNotifier):
    
    subject    = "This is a Template Test"
    recipients = ["Benjamin Bengfort <benjamin@unboundconcepts.com>",]

    html_template_name = "emails/test.html"
    text_template_name = "emails/test.txt"

    def get_context_data(self, **kwargs):
        context = super(TestTemplateNotifier, self).get_context_data(**kwargs)
        context['name'] = 'Benjamin Bengfort'
        context['body'] = 'This is other context data in the body.'
        return context

class TestManagerNotifier(ManagersNotifier):
    
    subject = "This is a Managers Notifier Test"
    
    html_template_name = "emails/test.html"
    text_template_name = "emails/test.txt"

    def get_context_data(self, **kwargs):
        context = super(TestManagerNotifier, self).get_context_data(**kwargs)
        context['name'] = 'Unbound Managers'
        context['body'] = 'This is other context data in the body.'
        return context

class TestUserNotifier(UserNotifier):
    
    subject = "This is a User Notifier Test"

    html_template_name = "emails/test.html"
    text_template_name = "emails/test.txt"
