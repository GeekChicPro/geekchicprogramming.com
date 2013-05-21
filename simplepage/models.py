from django.db import models
from tagging.fields import TagField
from django.utils.html import strip_tags
from tagging.utils import parse_tag_input
from django.contrib.markup.templatetags.markup import markdown
from django.contrib.markup.templatetags.markup import textile
from django.contrib.markup.templatetags.markup import restructuredtext

blank = {'null':True, 'blank':True, 'default':None}

MARKUPS = (
    ('HT', 'HTML'),
    ('MD', 'Markdown'),
    ('TT', 'Textile'),
    ('RE', 'RestructuredText'),
)

class Section(models.Model):
    """
    Defines the breadcrumbs and the related pages for sidebars.
    """

    name   = models.CharField( max_length=100, unique=True )
    parent = models.ForeignKey( 'self', related_name="children", **blank )
    lander = models.ForeignKey( 'SimplePage', related_name="+", **blank )

    @property
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root

    @property
    def breadcrumb_list(self):
        breadcrumbs = []
        parent = self
        while parent:
            breadcrumbs.append(parent)
            parent = parent.parent
        breadcrumbs.reverse()
        return breadcrumbs

    def get_absolute_url(self):
        if self.lander:
            return self.lander.get_absolute_url()
        return None

    def __len__(self):
        # pages is the related name from the RelatedPages model
        return self.pages.count()

    def __unicode__(self):
        return self.name.title()

class BaseSimplePage(models.Model):

    # Basic Properties 
    name    = models.CharField( max_length=100, unique=True)                    # Used for reverse
    body    = models.TextField( )                                               # The page body
    markup  = models.CharField( max_length=2, choices=MARKUPS, default='HT' )   # Type of Markup
    created = models.DateTimeField( auto_now_add=True )                         # Created on
    updated = models.DateTimeField( auto_now=True )                             # Last Updated


    # Items for meta tags in the header
    title       = models.CharField( max_length=255, **blank )                   # The title tag
    author      = models.CharField( max_length=255, **blank )                   # meta name=author
    description = models.CharField( max_length=255, **blank )                   # meta name=description
    keywords    = TagField( )                                                   # meta name=keywords

    @property
    def keywords_list(self):
        """
        Return iterable list of tags.
        """
        return parse_tag_input(self.keywords)

    @property
    def to_html(self):
        mujump = {
            'MD': markdown,
            'TT': textile,
            'RE': restructuredtext,
        }

        if self.markup == 'HT': return self.body
        formatter = mujump[self.markup]
        return formatter(self.body)

    def __len__(self):
        return len(strip_tags(self.to_html).split())

    def __unicode__(self):
        if self.title: return self.title
        return u'%s: %s' % (self.name, self.updated.strftime("%c"))

    class Meta:
        abstract  = True
        app_label = 'simplepage'
        ordering  = ['-created', '-updated']
        verbose_name = 'page'
        verbose_name_plural = 'pages'

class RelatedSimplePage(models.Model):
    """
    Has relationships to other pages to construct sidebar.
    """

    section = models.ForeignKey( Section, related_name='pages' )
    related = models.ManyToManyField( 'self', blank=True, null=True, verbose_name='related pages' )

    class Meta:
        abstract = True

class SimplePage(BaseSimplePage, RelatedSimplePage):

    def get_absolute_url(self):
        # Temporary 
        if self.section and not self.section.lander == self:
            return "/%s/%s/" % (self.section.name, self.name)
        return "/%s/" % self.name
