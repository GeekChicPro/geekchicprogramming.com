from django.db import models
from markdown2 import Markdown
from django.utils import timezone
from tagging.fields import TagField
from events.managers import EventManager
from tagging.utils import parse_tag_input

class Event(models.Model):

    title      = models.CharField( max_length=255 )
    slug       = models.SlugField( max_length=255, unique_for_date='start_date' )
    start_date = models.DateTimeField()
    end_date   = models.DateTimeField()
    location   = models.ForeignKey("Location", related_name="events")
    keywords   = TagField()
    created    = models.DateTimeField( auto_now_add=True )
    updated    = models.DateTimeField( auto_now=True )

    # Extended Manager Class
    objects    = EventManager()

    @property
    def keywords_list(self):
        """
        Returns an interable list of tags.
        """
        return parse_tag_input(self.keywords)

    @models.permalink
    def get_absolute_url(self):
        start_date = self.start_date
        if timezone.is_aware(start_date):
            start_date = timezone.localtime(start_date)
        return ('WorkshopEventDetail', (), {
                'year': start_date.strftime('%Y'),
                'month': start_date.strftime('%m'),
                'day': start_date.strftime('%d'),
                'slug': self.slug,
            })

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ["-start_date",]
        get_latest_by = "start_date"
        index_together = [["slug", "start_date"]]

class Workshop(Event):

    content    = models.TextField( help_text="Enter text in Markdown format." )                          # Note this should be in Markdown!
    teachers   = models.ManyToManyField('auth.User', related_name="workshops_teaching", blank=True)      # Will use the bio from the profile
    assistants = models.ManyToManyField('auth.User', related_name="workshops_assisting", blank=True)     # Will use the bio from the profile
    price      = models.DecimalField( max_digits=7, decimal_places=2 )
    price_text = models.CharField( max_length=255 )

    def to_html(self):
        formatter = Markdown()
        return formatter.convert(self.content)

    def __unicode__(self):
        return "%s at %s" % (self.title, self.location.name)

class Location(models.Model):

    name    = models.CharField( max_length=255, unique=True )
    website = models.URLField( null=True, blank=True, default=None )
    contact = models.CharField( max_length=255, null=True, default=None, blank=True )
    address = models.TextField( null=True, default=None, blank=True )
    city    = models.CharField( max_length=60 )
    state   = models.CharField( max_length=3 )
    zipcode = models.IntegerField()
    sponsor = models.BooleanField( default=False )

    def to_sline(self):
        address = " ".join(self.address.split())
        return "%s; %s, %s, %s" % (address, self.city, self.state, self.zipcode)

    def to_html(self):
        markup = ('<div class="vcard">\n'
                  '\t<a class="location" href="%s" title="%s">%s</a>'
                  '\t<div class="adr">\n'
                  '\t\t<div class="street-address">%s</div>\n'
                  '\t\t<span class="locality">%s</span>, '
                  '\t\t<abbr class="region">%s</abbr>&nbsp;&nbsp;'
                  '\t\t<span class="postal-code">%s</span>\n'
                  '\t</div>'
                  '</div>')
        return markup % ( self.website, self.name, self.name,
                          self.address.replace("\n", "<br />"),
                          self.city, self.state, self.zipcode )

    def __unicode__(self):
        return self.name
