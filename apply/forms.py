from django import forms
from auth.models import Student
from events.models import Fellowship
from django.utils.translation import ugettext_lazy as _
from apply.models import FellowshipApplication, Enrollment
from geekchic.utils.forms.widgets import BootstrapRadioRenderer, BootstrapCheckboxSelectMultiple


class FellowshipApplicationForm(forms.ModelForm):
    """
    The much expanded form for the fellowship application. Although this
    extends Django's ModelForm, note that it does NOT behave like a one
    as it will save many models. You also won't be able to update an
    application from this form...

    @note: I hacked this together at a conference in NYC-- enjoy!
    """

    def __init__(self, *args, **kwargs):
        """
        Ensures auto_id is turned off, and that all widgets have an id
        attribute that matches their name instead of the id_field
        convention that Django uses.
        """

        kwargs['auto_id'] = False
        super(FellowshipApplicationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items( ):
            if isinstance(field.widget, forms.RadioSelect):
                continue
            elif isinstance(field.widget, BootstrapCheckboxSelectMultiple):
                continue

            field.widget.attrs.update({'id': name})

            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'rows':10, 'class':'span8'})
            else:
                field.widget.attrs.update({'class':'span5'})

    first_name = forms.CharField( max_length=40, label="First Name" )
    last_name  = forms.CharField( max_length=40, label="Last Name" )
    email      = forms.EmailField()
    twitter    = forms.CharField( max_length=40, label="Twitter Handle", initial="@" )
    linkedin   = forms.URLField( max_length=255, label="LinkedIn Profile" )

    def clean_twitter(self):
        """
        Ensures the twitter handle starts with '@' and there is more than
        two characters in the username.
        """
        data = self.cleaned_data['twitter']
        if not data.startswith('@'):
            raise forms.ValidationError("Twitter usernames must start with '@'.")
        if len(data) <= 1:
            raise forms.ValidationError("Please supply a twitter username.")
        return data

    def clean_linkedin(self):
        """
        Ensures that the domain linkedin.com is somewhere in the string...
        yeh, I know that won't validate 100% of the time, but let's hope
        for the best.
        """
        data = self.cleaned_data['linkedin']
        if "linkedin.com" not in data:
            raise forms.ValidationError("Please provide a link to LinkedIn.")
        return data

    def clean(self):
        """
        Hook for after field validation cleaning for validating objects
        that depend on each other. In this instance the applicant and the
        application semester.
        """
        cleaned_data = super(FellowshipApplicationForm, self).clean()

        semesters    = cleaned_data.get('semesters', [])
        email        = cleaned_data.get('email', None)

        if not email or not semesters:
            return cleaned_data

        students     = Student.objects.filter(email=email)
        applications = FellowshipApplication.objects.filter(semesters__in=semesters) \
                            .filter(applicant__in=students).count()

        if applications > 0:
            raise forms.ValidationError("It appears that an applications for one or more "
                                        "of the listed semesters already exists for %s. "
                                        "Please contact the administrators with the contact "
                                        "form if you need assistance (which is better than simply "
                                        "using an alternate email)."
                                        % email)

        return cleaned_data

    def save(self, commit=True):
        """
        Does not use `construct_instance` and `save_instance` -- you'll
        have to use another form to update the model...
        """
        if not commit:
            raise Exception("Sorry, this form has to be committed to the database when saved.")

        instance = self.instance
        opts = instance._meta
        if self.errors:
            raise ValueError("The %s could not be created because the data didn't"
                             " validate." % (opts.object_name) )

        cleaned_data = self.cleaned_data

        user_data = {
            'first_name': cleaned_data.pop('first_name'),
            'last_name': cleaned_data.pop('last_name'),
            'email': cleaned_data.pop('email'),
        }

        links_data = {
            'twitter': {
                'href': "https://.twitter.com/" + cleaned_data.pop('twitter').replace("@", ""),
                'target': "TW",
            },
            'linkedin': {
                'href': cleaned_data.pop('linkedin'),
                'target': "LI",
            }
        }

        # Get or create the user/student object.
        try:
            # Note: email is not unique-- if someone has stored the same
            # email in two profiles, this will fail pretty hard!
            applicant = Student.objects.get(email=user_data['email'])

            # Update user information:
            for key, val in user_data.items():
                setattr(applicant, key, val)
            applicant.save()
        except Student.DoesNotExist:
            applicant = Student.objects.create_with_username(**user_data)

        # Add Links
        for key, kwargs in links_data.items():
            if not applicant.profile.get_link(key):
                applicant.profile.links.create(**kwargs)

        # Validate User/Semester applications uniqueness.
        semesters = cleaned_data.pop('semesters')

        # Save Application
        cleaned_data['applicant'] = applicant
        application = FellowshipApplication.objects.create(**cleaned_data)

        for semester in semesters:
            Enrollment.objects.create(semester=semester, application=application)

        return application

    class Meta:
        model   = FellowshipApplication
        fields  = ('semesters', 'first_name', 'last_name', 'email', 'twitter',
                   'linkedin', 'computer', 'education', 'experience', 'skills', 'reason',
                   'project', 'bragging', 'dream_job', 'riddle', 'video', 'pay_method',
                   'recommender', 'heard_about',)
        widgets = {
            'semesters': BootstrapCheckboxSelectMultiple(),
            'computer': forms.RadioSelect(renderer=BootstrapRadioRenderer, attrs={'inline': True}),
            'pay_method': forms.RadioSelect(renderer=BootstrapRadioRenderer)
        }
