import urllib
import hashlib

from django.db import models
from django.contrib.auth.models import User
from managers import AuthorManager
from django.utils.translation import ugettext_lazy as _

class AuthorProfile(models.Model):

    user      = models.OneToOneField( User, editable=False, related_name="profile" )
    biography = models.TextField( blank=True, null=True, default=None )
    shortbio  = models.CharField( max_length=156, blank=True, null=True, default=None )

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

    def delete(self, using=None):
        self.user.delete(using=using)
        super(AuthorProfile, self).delete(using=using)

    def __unicode__(self):
        return self.full_email

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        db_table = "auth_profile"

SOCIAL_LINK_TYPES = (
    ("D", "Delicious"),
    ("DG", "Digg"),
    ("FB", "Facebook"),
    ("FL", "Flickr"),
    ("G", "Google"),
    ("LI", "LinkedIn"),
    ("P", "Picasa"),
    ("R", "Reddit"),
    ("RS", "RSS"),
    ("SU", "Stumble Upon"),
    ("TI", "Technorati"),
    ("TR", "Tumblr"),
    ("TW", "Twitter"),
    ("V", "Vimeo"),
    ("Y", "Yahoo"),
    ("YT", "YouTube"),
)

class AuthorLink(models.Model):

    profile = models.ForeignKey( AuthorProfile, related_name="links" )
    href    = models.URLField( verbose_name="URL" )
    target  = models.CharField( max_length=2, choices=SOCIAL_LINK_TYPES )

    def get_css_class(self):
        target = self.get_target_display().lower().replace(" ", "_")
        return target

    def get_css_title(self):
        return self.get_target_display()

    def __unicode__(self):
        return self.href

    class Meta:
        db_table = "auth_profile_link"
        verbose_name = _('link')
        verbose_name_plural = _('links')

######################################################################
## Django User Model Proxy
######################################################################

class Author(User):
    """
    Proxy class for django.contrib.auth.models.User for enacting our
    methods and management on the User database without affecting the
    User class.
    """

    objects = AuthorManager()

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

    class Meta:
        proxy= True