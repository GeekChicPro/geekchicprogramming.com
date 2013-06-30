from events.models import Workshop
from django.template import Library
from django.db.models import Q

register = Library()

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_author_entries(context, number=5, template='zinnia/tags/recent_entries.html'):
    """Return the most recent entries for the author."""
    return {'template': template,
            'entries': context['student'].get_author().entries_published()[:number]}

@register.inclusion_tag('zinnia/tags/dummy.html', takes_context=True)
def get_workshops_teaching(context, number=5, template='tags/recent_events.html'):
    """
    Returns the most recent workshops taught or assisted for the user.
    """
    s = context['student']
    return {
        'template': template,
        'events': Workshop.objects.filter(Q(teachers__in=[s]) | Q(assistants__in=[s]))[:number],
    }