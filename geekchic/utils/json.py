from django.views.generic import View
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.views.generic.edit import BaseFormView
from django.utils import simplejson
from django.utils.encoding import force_text
from django.db.models.base import ModelBase
from django.db.models import ManyToManyField
from django.http import HttpResponseNotAllowed, HttpResponse 
from django.core.exceptions import ImproperlyConfigured

def dumps(content, json_opts={}):
    """
    Replaces simplejson.dumps with our own custom encoder
    """
    json_opts['ensure_ascii'] = json_opts.get('ensure_ascii', False)
    json_opts['cls'] = json_opts.get('cls', LazyJSONEncoder)

    return simplejson.dumps(content, **json_opts)

class LazyJSONEncoder(simplejson.JSONEncoder):
    """ 
    A JSONEncoder subclass that handles querysets and model objects.
    If the model object has a "serialize" method that returns a dictionary,
    then this method is used, else, it attempts to serialize fields. 
    """

    def default(self, obj):
        # This handles querysets and other iterable types
        try:
            iterable = iter(obj)
        except TypeError: 
            pass
        else:
            return list(iterable) 

        # This handles Models
        if isinstance(obj.__class__, ModelBase):
            if hasattr(obj, 'serialize') and callable(getattr(obj, 'serialize')):
                return obj.serialize()
            return self.serialize_model(obj)

        # Other Python Types:
        try:
            return force_text(obj)
        except Exception:
            pass

        # Last resort:
        return super(LazyJSONEncoder, self).default(obj)

    def serialize_model(self, obj):
        tmp = { }
        many = [f.name for f in obj._meta.many_to_many]
        for field in obj._meta.get_all_field_names( ):
            if len(many) > 0 and field in many:
                many.remove(field)
                tmp[field] = getattr(obj, field).all( )
            else:
                tmp[field] = getattr(obj, field, None)
        return tmp

class JSONResponse(HttpResponse):

    def __init__(self, content='', json_opts={}, mimetype="application/json", *args, **kwargs):
        
        if content:
            content = dumps(content, json_opts)
        else:
            content = dumps([ ], json_opts)

        super(JSONResponse, self).__init__(content,mimetype,*args,**kwargs)
        self['Cache-Control'] = 'max-age=0,no-cache,no-store'

    @property
    def json(self):
        return simplejson.loads(self.content)

class JSONResponseMixin(object):
    
    def render_to_response(self, context, *args, **kwargs):
        return JSONResponse(context, *args, **kwargs)

    def remove_duplicate_obj(self, context, duplicate="object", **kwargs):
        # Check if the duplicate key is in the context
        if duplicate in context:
            # Search to ensure that this key is in fact duplicated
            for key, val in context.items():
                if key == duplicate: continue           # Skip the duplicate object
                if val == context[duplicate]:
                    del context[duplicate]
                    break

        return context

class JSONDataView(JSONResponseMixin, View):

    def get_context_data(self, **kwargs):
        return kwargs

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class JSONDetailView(JSONResponseMixin, BaseDetailView):
    """
    Override get method to allow access from querystrings for AJAX calls.
    """

    def get(self, request, **kwargs):
        """
        This method does not allow multiple parameters in the query string, 
        so a normal dictionary rather than a QueryDict is necessary. 

        The development version has a QuerySet.dict method-- but not 1.3, so
        we have to do this manually until the new version comes out. 
        """
        querydict = dict([(k,v) for k,v in request.GET.iteritems()])
        self.kwargs.update(querydict)
        kwargs.update(querydict)
        return super(JSONDetailView, self).get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JSONDetailView, self).get_context_data(**kwargs)
        return self.remove_duplicate_obj(context)

class JSONListView(JSONResponseMixin, BaseListView):

    def get_context_data(self, **kwargs):
        context = super(JSONListView, self).get_context_data(**kwargs)
        return self.remove_duplicate_obj(context, duplicate="object_list")

class PaginatedJSONListView(JSONListView):
    """
    Provides some helper view methods and a default pagination for the
    ListView -- including removal of pagination data from the json and a
    json return of the total number of results and pages that will be 
    returned on the submission of a get request. 
    """

    paginate_by = 10
    count_query = 'count'
    count_only  = False

    def get_count_query(self):
        return self.count_query

    def get_count_only(self):
        return self.count_only

    def get(self, request, *args, **kwargs):
        """
        On GET if the parameter defined by ``count_query`` is in the 
        request, then set the count only parameter to True. Note that the
        method ``get_count_only`` can override or use this value as
        required -- but the interface is to set the value on the instance.
        """
        if self.get_count_query() in self.request.GET:
            self.count_only = True
        return super(PaginatedJSONListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Removes paginator objects and instead supplies the pages and the
        count data as part of the paginated framework. Leaves in the 
        ``is_paginated`` boolean value. 

        Also tests to see if get_count_only is True -- if so, it returns
        only the pages and the count rather than the entire context.
        """
        context = super(PaginatedJSONListView, self).get_context_data(**kwargs)

        # Replace paginatior data with JSON friendly data
        page       = context.pop('page_obj')
        paginator  = context.pop('paginator')
        count_only = self.get_count_only()

        if paginator:
            pages = paginator.num_pages
            count = paginator.count
            ispag = page.has_other_pages()
            ppage = paginator.per_page 
        else:
            # Honestly, this should never happen.
            pages = 1
            count = self.get_queryset().count()  # This should be the object_list that comes through... 
            ispag = False
            ppage = count

        if count_only:
            return { 'pages':pages, 
                     'count':count, 
                     'per_page': ppage,
                     'is_paginated': ispag }
        else:
            context['pages'] = pages
            context['count'] = count

        return context

class JSONFormView(JSONResponseMixin, BaseFormView):
    """
    An attempt to integrate a JSONView with a FormView. 

    Basically, the idea is this- JSON views will not require a GET method.
    Since POST is the only concern, we need to pass the post data into
    the form, then respond with JSON data instead of Form data. 

    Several Overrides are the attempt to manipulate the BaseFormView to
    respond with JSON data, rather than starting from scratch. 
    """

    def get_form_class(self):
        """
        There will be issues if form_class is None, so override this 
        method to check and see if we have one or not.
        """
        form_class = super(JSONFormView, self).get_form_class()
        if form_class is None:
            raise ImproperlyConfigured(
                "No form class to validate. Please set form_class on"
                " the view or override 'get_form_class()'.")
        return form_class

    def get_success_url(self):
        """
        Overridden to ensure that JSON data gets returned, rather 
        than HttpResponseRedirect, which is bad.
        """
        return None

    def form_valid(self, form):
        """
        Overridden to ensure that an HttpResponseRedirect does not get
        called with a success_url -- instead render_to_response some
        JSON data. DO NOT CALL SUPER!

        @note: We return a JSON flag - { success: true }. Because this
        is a common paradigm in Ben programming. However, it seems that
        the flag should be { valid: true }. Discuss amongst yourselves.
        """
        return self.render_to_response(self.get_context_data(success=True))

    def form_invalid(self, form):
        """
        Overridden to ensure that a form object isn't returned, since
        that has some weird serialization issues. Instead pass back
        the errors from the form, and a JSON flag - { success: false }.

        @note: See form_valid for more discussion on the JSON flag.
        """
        context = self.get_context_data(success=False)
        context['errors'] = form.errors 
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        """
        Overridden so that on a GET request the response isn't allowed.

        JSON Forms are intrinsinctly POST driven things, a GET makes
        no sense in the context of a form. (What would you get?). For
        Normal HTTP, you would pass back an empty form, but that's 
        pretty usesless for JSON. So we pwn this entire method right
        off the bat to ensure no screwiness or excessive net traffic.
        """
        return HttpResponseNotAllowed(['GET',])
