"""
Contains class based views available to the feedback module.

@author: U{Benjamin Bengfort<mailto:benjamin@bengfort.com>}

@requires: Python 2.7
@requires: Django 1.5.1

@version: 1.0
@change: I{views.py [43] benjamin@bengfort.com}
@since: Tue Mar 13 23:21:37 2012 -0400
"""
__docformat__ = "epytext en"

###################################################################### 
## Imports 
###################################################################### 

from django.contrib import messages
from feedback.forms import ContactForm
from django.views.generic import FormView
from django.core.urlresolvers import reverse
from feedback.models import Feedback

class ContactFormView(FormView):
    """
    A Web View that allows an email contact form to be displayed and 
    on successful completion of the form, sends the email to the managers.

    @ivar template_name: The name of a template that renders the form
    @ivar form_class: The class of the contact form 
    @ivar success_url: Where to redirect the user when the form is sent.
    """
    template_name = "contact.html"
    form_class    = ContactForm
    success_url   = None

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
            return reverse('contact')

    def form_valid(self, form):
        """
        If the form is valid, e.g. all the fields are filled out correctly
        then send an email to the Managers concerning the feedback, and 
        forward a copy to the user if requested. Create a message using
        the django.contrib.messages app to display on the contact form. 

        @return: The response with the message attached
        @rtype: C{HttpResponse}
        """
        if form.send():
            messages.success(self.request, "Thanks for your email, we'll respond shortly!")
        return super(ContactFormView, self).form_valid(form)
