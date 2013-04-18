from django.views.generic import TemplateView
from django.http import Http404

MODULES = {
    'one': {
        'name': 'Your Development Environment',
        'presentation': 'An Introduction to the Workshop',
        'workshop': 'Setting up your Development Environment',
    },
    'two': {
        'name': 'The Command Line',
        'presentation': 'Executing Programs without a Double Click',
        'workshop': 'Getting to know Your Real Computer',
    },
    'three': {
        'name': 'Programming Basics',
        'presentation': 'Girl(name="Jane Doe").code()',
        'workshop': 'Move over, Trinity',
    },
    'four': {
        'name': 'The Web Front and HTML',
        'presentation': 'Marking Stuff Up',
        'workshop': 'Writing for the Web without Bloggging',
        'handout': 'HTML Tags',
    },
    'five': {
        'name': 'Writing a Web Application with Django',
        'presentation': 'The Money Maker, Django',
        'workshop': 'Your First Web App (Twitter is Easy!)',
    },
}

class ScheduleView(TemplateView):
    
    template_name = "schedule.html"

class SyllabusView(TemplateView):

    template_name = "syllabus.html"

    def get_context_data(self, **kwargs):
        context = super(SyllabusView, self).get_context_data(**kwargs)
        context['modules'] = MODULES
        return context

class ModuleView(TemplateView):

    def get_template_names(self, *args, **kwargs):
        module  = self.kwargs['module']
        doctype = self.kwargs['doctype']

        valid_modules  = ('one', 'two', 'three', 'four', 'five')
        valid_doctypes = ('presentation', 'workshop', 'handout')

        if module not in valid_modules or doctype not in valid_doctypes:
            raise Http404

        return "module_%s/%s.html" % (module, doctype)

    def get_context_data(self, **kwargs):
        context = super(ModuleView, self).get_context_data(**kwargs)

        context['module']  = self.kwargs['module']
        context['doctype'] = self.kwargs['doctype']
        context.update(MODULES[context['module']])

        return context
