import logging
from django.http import Http404
from django.views.generic import CreateView
from followers.models import Follower
from followers.notify import send_signup
from geekchic.utils.json import JSONResponseMixin

class AddFollower(JSONResponseMixin, CreateView):

    model = Follower
    success_url = '/'

    def get(self, request, *args, **kwargs):
        raise Http404

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(success=False, form=form))

    def form_valid(self, form):
        self.instance = form.save( )
        # Notify User and Managers
        send_signup(self.instance.name, self.instance.email)
        return self.render_to_response(self.get_context_data(success=True, form=form))
