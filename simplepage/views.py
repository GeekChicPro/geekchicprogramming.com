# Create your views here.

from models import SimplePage
from django.views.generic import DetailView

class SimplePageView(DetailView):
    
    model = SimplePage
    template_name = 'simplepage.html' 
    slug_field = 'name'
    slug_url_kwarg = 'name'
