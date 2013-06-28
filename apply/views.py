from apply.forms import FellowshipApplicationForm
from events.models import Fellowship
from django.views.generic import FormView, TemplateView
from django.contrib import messages
from apply.notify import notify_applicant, notify_managers

HEADING = 50

class FellowshipApplicationView(FormView):

    form_class = FellowshipApplicationForm
    template_name = "forms/apply.html"
    success_url = "/apply/submitted/"

    def form_valid(self, form):
        # Save the data to the database
        self.object = form.save( )

        # Notify the managers and applicants
        # This will take time, should probably thread
        notify_applicant(self.object)
        notify_managers(self.object)

        # Prepare messages for next view and render
        applicant_name = "%s %s" % (self.object.applicant.first_name, self.object.applicant.last_name)
        semesters = " and ".join([semester.semester for semester in self.object.semesters.all()])
        messages.add_message(self.request, HEADING, "Thanks for applying, %s!" % applicant_name )
        messages.add_message(self.request, messages.INFO, "We've received your application for the %s semesters, and will be in touch with you shortly." % semesters)
        return super(FellowshipApplicationView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(FellowshipApplicationView, self).get_context_data(**kwargs)
        context['fellowships'] = Fellowship.objects.order_by('start_date')
        return context

class ApplicationSubmitted(TemplateView):

    template_name = "application-submitted.html"