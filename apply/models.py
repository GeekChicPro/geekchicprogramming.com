from django.db import models
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.utils.html import linebreaks

class Application(models.Model):

    applicant = models.ForeignKey('auth.User', related_name="applications")
    created   = models.DateTimeField( auto_now_add=True )
    updated   = models.DateTimeField( auto_now=True )

    class Meta:
        abstract = True
        ordering = ["-created",]
        get_latest_by = "created"

RIDDLE = ("Optional Riddle: You have twelve coins, eleven identical and one different. "
          "You do not know whether the \"odd\" coin is lighter or heavier than the others. "
          "Someone gives you a balance and three chances to use it. The question is: How "
          "can you make just three weighings on the balance and find out not only which "
          "coin is the \"odd\" coin, but also whether it's heavier or lighter?")

class FellowshipApplication(Application):

    COMPUTER_TYPES = (
        ('Mac', 'MacBook'),
        ('Mbp', 'MacBook Pro'),
        ('WinN', 'Windows 7 or Newer'),
        ('WinO', 'Windows Vista or Older'),
        ('Lnx', 'Linux Laptop'),
    )

    TUITION_PAYMENT_METHODS = (
        ("U", "Upfront"),
        ("M", "Monthly"),
        ("F", "Financial Aid"),
    )

    semesters   = models.ManyToManyField( 'events.Fellowship',
                    through="Enrollment", related_name="applications",
                    verbose_name="What semesters are you applying to?", )
    semesters.help_text = "You may apply to more than one semester."

    computer    = models.CharField( max_length=4, choices=COMPUTER_TYPES,
                    default="Mac", verbose_name="What type laptop will you be developing on?" )
    computer.help_text="You will need some kind of development computer that meets a minimum technology requirement, and is probably 2 or 3 years old or newer. See more details on the Fellowship requirements page."

    education   = models.TextField( verbose_name="Your education details." )
    education.help_text="In a couple of sentences, describe where and when you went to school, and what you learned."

    experience  = models.TextField( verbose_name="Your experience." )
    experience.help_text="We'll look at your resume on LinkedIn, just highlight interesting places you've been and projects you've worked on. We'd like to get a sense of where you are in life- something a resume can't tell us."

    skills      = models.TextField( verbose_name="What are your tech skills?" )
    skills.help_text="Programming skills, nunchuck skills, design skills, etc. From beginner to advanced, just let us know!"

    reason      = models.TextField( verbose_name="What do you want to get out of this Fellowship?" )
    reason.help_text="Be honest, we really want to know what you want to get out of this- so we can try to make it happen!"

    project     = models.TextField( verbose_name="Do you have a project? Please describe it!" )
    project.help_text="If you start with a goal, it's easier to achieve. Plus you'll have expert help for ten weeks!"

    bragging    = models.TextField( verbose_name="Brag about yourself!" )
    bragging.help_text = "Don't be afraid to really show off, give us your best shot!"

    dream_job   = models.TextField( verbose_name="Describe your dream job." )

    riddle      = models.TextField( blank=True, null=True, default=None,
                    verbose_name=RIDDLE )
    riddle.help_text = "Don't worry if it's right or wrong, we really want to know how you think."

    video       = models.URLField( blank=True, null=True, default=None,
                    verbose_name="Optional Video" )
    video.help_text = "You may optionally provide a link to a short video introducing yourself and making a case for why you should be part of the next GeekChic Fellowship. Short and simple is fine, about three minutes, and we're more interested in content than quality."

    pay_method  = models.CharField( max_length=1, choices=TUITION_PAYMENT_METHODS, default="U",
                    verbose_name="How will you pay?" )

    recommender = models.EmailField( blank=True, null=True, default=None,
                    verbose_name="Optional Recommendation" )
    recommender.help_text = "Please provide the email address of someone we can contact who will recommend you."

    heard_about = models.CharField( max_length=255, verbose_name="How did you hear about us?",
                    blank=True, null=True, default=None )
    appfee_paid = models.BooleanField( default=False, verbose_name="Application Fee Paid?" )

    def pprint(self):
        """
        Pretty prints the application in text.
        """
        format = {
            'full_email' : self.applicant.profile.full_email,
            'twitter'    : self.applicant.profile.get_link("twitter"),
            'linkedin'   : self.applicant.profile.get_link("linkedin"),
            'computer'   : self.get_computer_display(),
            'semesters'  : "\n    * ".join([str(f) for f in self.semesters.all()]),
            'pay_method' : self.get_pay_method_display(),
        }

        fields = ( 'education', 'experience', 'skills', 'reason',
                   'project', 'bragging', 'dream_job', 'riddle', 'video',
                   'recommender', 'heard_about', 'appfee_paid', )

        output = ("Application from: %(full_email)s\n"
                  "Twitter: %(twitter)s\n"
                  "Linked In: %(linkedin)s\n\n"
                  "Applied to the following semesters:\n"
                  "%(semesters)s\n\n"
                  "Application Details:\n\n"
                  "Computer: %(computer)s\n"
                  "Pay method: %(pay_method)s\n\n" % format)

        for field in fields:
            answer = getattr(self, field)
            afield = self._meta.get_field_by_name(field)[0]
            things = (afield.verbose_name, answer)
            output += "Question: %s\nAnswer: %s\n\n" % things

        return output

    def pprint_html(self):
        return linebreaks(self.pprint())

    class Meta:
        db_table = "fellowship_applications"

class Enrollment(models.Model):

    application  = models.ForeignKey('FellowshipApplication')
    semester     = models.ForeignKey('events.Fellowship', related_name="enrollment")
    accepted     = models.BooleanField( default=False )
    date_decided = models.DateTimeField( null=True, default=None )
    early_decide = models.BooleanField( default=False )
    tuition_paid = models.DecimalField( max_digits=7, decimal_places=2, default=Decimal('0.00') )

    class Meta:
        db_table = "fellowship_enrollment"
