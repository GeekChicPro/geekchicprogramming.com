from django import forms
from django.utils.safestring import mark_safe
from geekchic.utils.notify import ManagersNotifier, TemplateNotifier

FIELDS_HELP = (
    ('sender', 'Your name, so we know who you are!'),
    ('email', 'Your email, so we can respond!'),
    ('subject', 'Let us know what\'s up!'),
    ('message', 'Qestions, comments, concerns, and compliments are welcome!'),
    ('ccme', ''),
)

CONTACT_EMAIL_TEMPLATE = "emails/contact-manager-email.html"
CONTACT_EMAIL_TEXT_TEMPLATE = "emails/contact-manager-email.txt"
CC_EMAIL_TEMPLATE = "emails/cc-email.html"
CC_EMAIL_TEXT_TEMPLATE = "emails/cc-email.txt"

class BootstrapCheckboxInput(forms.widgets.CheckboxInput):

    def __init__(self, *args, **kwargs):

        self.choice_label = kwargs.pop('choice_label', '')
        super(BootstrapCheckboxInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        tag = super(BootstrapCheckboxInput, self).render(name, value, attrs)
        return mark_safe(u'<label class="checkbox">%s %s</label>' % (tag, self.choice_label))

class ContactForm(forms.Form):

    sender  = forms.CharField(max_length=100)
    email   = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows':'12'}))
    ccme    = forms.BooleanField(required=False, label="", widget=BootstrapCheckboxInput(choice_label="Send me a copy"))

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        for field_help in FIELDS_HELP:
            self.fields[field_help[0]].help_text = field_help[1]
            self.fields[field_help[0]].widget.attrs.update({'class':'input-xxlarge'})

    def clean_subject(self):

        subject = self.cleaned_data.get('subject', '').strip()
        return "GeekChic Contact: %s" % subject

    def clean_sender(self):
        return self.cleaned_data.get('sender', '').strip()

    def send(self):
        """
        Called when the form is sucessfully validated (hopefully)
        """

        sender     = self.cleaned_data.get('sender')
        email      = self.cleaned_data.get('email')
        subject    = self.cleaned_data.get('subject')
        message    = self.cleaned_data.get('message')
        ccsender   = self.cleaned_data.get('ccme')


        # Construct the Managers Notifer
        notifier = ManagersNotifier( subject=subject,
                                     html_template_name = CONTACT_EMAIL_TEMPLATE,
                                     text_template_name = CONTACT_EMAIL_TEXT_TEMPLATE )

        # Dispatch the notification with the cleaned_data as context
        notifier.dispatch(**self.cleaned_data)

        # If a copy was requested to be sent to the user, send it.
        if ccsender:

            from_email = "%s <%s>" % (sender, email)

            ccnotifier = TemplateNotifier( subject=subject,
                                         recipients=(from_email,),
                                         html_template_name = CC_EMAIL_TEMPLATE,
                                         text_template_name = CC_EMAIL_TEXT_TEMPLATE )
            ccnotifier.dispatch(**self.cleaned_data)

        # TODO: Determine if something went wrong and return an error
        return True
