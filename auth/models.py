import urllib
import hashlib

from django.db import models
from django.contrib.auth.models import User
from managers import StudentManager
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals
from auth.signals import create_profile
from zinnia.models import Author

class UserProfile(models.Model):

    user       = models.OneToOneField( User, editable=False, related_name="profile" )
    biography  = models.TextField( blank=True, null=True, default=None )
    shortbio   = models.CharField( max_length=156, blank=True, null=True, default=None )
    is_teacher = models.BooleanField( _("teacher or tutor"), default=False )
    is_tassist = models.BooleanField( _("teaching assistant"), default=False )

    @property
    def gravatar(self):
        size    = 120
        default = "mm"
        digest  = hashlib.md5(self.user.email.lower()).hexdigest()
        params  = urllib.urlencode({'d':default, 's':str(size)})
        gravurl = "http://www.gravatar.com/avatar/%s?%s" % (digest, params)
        return gravurl

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def full_email(self):
        email = "%s <%s>" % (self.full_name, self.user.email)
        return email.strip()

    def get_link(self, name):
        """
        Fetches a link via the type, if the link doesn't exist, then it
        returns None -- note an error is rasied if the name isn't in the
        SOCIAL_LINK_TYPES below.
        """
        link_type = ProfileLink.type_from_name(name)
        try:
            return ProfileLink.objects.get(profile=self, target=link_type)
        except ProfileLink.DoesNotExist:
            return None

    def delete(self, using=None):
        self.user.delete(using=using)
        super(UserProfile, self).delete(using=using)

    def __unicode__(self):
        return self.full_email

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        db_table = "auth_profile"

SOCIAL_LINK_TYPES = (
    ("BL", "Blogger"),
    ("D", "Delicious"),
    ("DG", "Digg"),
    ("Dr", "Dribble"),
    ("FB", "Facebook"),
    ("FL", "Flickr"),
    ("FR", "Forrst"),
    ("GH", "Github"),
    ("G", "Google"),
    ("IG", "Instagram"),
    ("LI", "LinkedIn"),
    ("P", "Pinterest"),
    ("R", "Reddit"),
    ("RS", "RSS"),
    ("ST", "ShareThis"),
    ("Sy", "Skype"),
    ("SU", "Stumble Upon"),
    ("TR", "Tumblr"),
    ("TW", "Twitter"),
    ("V", "Vimeo"),
    ("WP", "Wordpress"),
    ("YT", "YouTube"),
    ("O", "Other"),
)

class ProfileLink(models.Model):

    profile = models.ForeignKey( UserProfile, related_name="links" )
    href    = models.URLField( verbose_name="URL" )
    target  = models.CharField( max_length=2, choices=SOCIAL_LINK_TYPES )

    # To reverse link type from names
    _name_link_map = dict([(ltype[1].lower(), ltype[0]) for ltype in SOCIAL_LINK_TYPES])

    @classmethod
    def type_from_name(klass, name):
        name = name.lower()
        if name not in klass._name_link_map:
            raise KeyError("'%s' is not in the SOCIAL_LINK_TYPES enumeration" % name)
        return klass._name_link_map[name]

    def get_css_class(self):
        target = self.get_target_display().lower().replace(" ", "-")
        return target

    def get_css_title(self):
        return self.get_target_display()

    def __unicode__(self):
        return self.href

    class Meta:
        db_table = "auth_profile_link"
        verbose_name = _('link')
        verbose_name_plural = _('links')
        unique_together = (("profile", "target"),)

######################################################################
## Django User Model Proxy
######################################################################

class Student(User):
    """
    Proxy class for django.contrib.auth.models.User for enacting our
    methods and management on the User database without affecting the
    User class.
    """

    objects = StudentManager()

    @classmethod
    def fromUser(klass, user):
        return klass.objects.get(pk=user.pk)

    @property
    def gravatar(self):
        size    = 120
        default = "mm"
        digest  = hashlib.md5(self.email.lower()).hexdigest()
        params  = urllib.urlencode({'d':default, 's':str(size)})
        gravurl = "http://www.gravatar.com/avatar/%s?%s" % (digest, params)
        return gravurl

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def full_email(self):
        return self.get_profile().full_email

    def get_author(self):
        return Author.objects.get(pk=self.pk)

    class Meta:
        proxy= True

######################################################################
## Ensure that when a Student or User is created, a Profile is too.
######################################################################

signals.post_save.connect(create_profile, sender=User)
signals.post_save.connect(create_profile, sender=Student)
