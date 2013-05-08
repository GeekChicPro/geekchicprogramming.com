from django.core.mail import EmailMultiAlternatives

def send_html(subject, text, html, from_email, recipient_list, fail_silently=False, connection=None):
    mail = HtmlEmail(subject=subject,
                     text=text,
                     html=html,
                     from_email=from_email,
                     to=recipient_list,
                     connection=connection)
    mail.send(fail_silently=fail_silently)


class HtmlEmail(EmailMultiAlternatives):
    """
    Easy setup of a dual text/html message by either overriding the
    get_text_content or get_html_content methods, or by simply setting
    the html_content and text_content class variables.
    """

    text_content = None
    html_content = None

    def __init__(self, **kwargs):
        
        self.text_content = kwargs.pop('text', None)
        self.html_content = kwargs.pop('html', None)

        # Construct plain text email with super.
        if 'body' not in kwargs:
            kwargs['body'] = self.get_text_content()

        super(HtmlEmail, self).__init__(**kwargs)

        # Attach HTML content
        self.attach_alternative(self.get_html_content(), "text/html")

    def get_text_content(self, **kwargs):
        if self.text_content is None:
            raise NotImplementedError("Subclass with text_content, override this method, or set before instantiation")
        return self.text_content

    def get_html_content(self, **kwargs):
        if self.html_content is None:
            raise NotImplementedError("Subclass with html_content, override this method, or set before instantiation")
        return self.html_content
