from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect

class DispatchProtectionMixin(object):
    
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(DispatchProtectionMixin, self).dispatch(*args, **kwargs)

class LoginRequiredMixin(object):
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class CsrfExemptMixin(object):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(*args, **kwargs)
