import os
import csv

from auth.models import Student
from optparse import make_option
from django.db import connection
from auth.utils import generate_password
from auth.notify import send_registration
from django.core.management.base import LabelCommand, CommandError

class Command(LabelCommand):

    label = "Attendees CSV"

    option_list = LabelCommand.option_list + (
        make_option('-p', action='store', default=7, type='int', dest='password_length',
            help='Set the length of the generated password'),
        make_option('-e', '--noemail', action='store_true', dest='noemail',
            help='Do not notify users by email'),
    )

    def expand_path(self, path):
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        return path

    def create_user(self, first_name, last_name, email):
        password = generate_password()
        student  = Student.objects.create_with_username(
                        first_name= first_name.title(),
                        last_name = last_name.title(),
                        email     = email.lower(),
                        password  = password)

        if self.verbosity > 1:
            print student.full_email
            print "U: %s P: %s" % (student.username, password)

        self.count += 1

        return student, password

    def notify_user(self, user, password=None):
        success = send_registration(user, password)

        if self.verbosity > 1:
            if success:
                print "Email notification sent successfully"
            else:
                print "Could not send email!!"

    def handle(self, *args, **options):

        # Handle Options
        self.password_length = options.get('password_length', 7)
        self.verbosity = int(options.get('verbosity'))
        self.notify    = not options.get('noemail')

        # Output options
        self.count  = 0
        self.errors = 0

        args = list(args)
        for idx, arg in enumerate(args):
            arg = self.expand_path(arg)
            if not os.path.isfile(arg):
                raise CommandError("Please specify a correct path to a %s" % self.label)
            args[idx] = arg

        # Handle Arguments
        super(Command, self).handle(*args, **options)

        if self.verbosity > 0:
            print "%i users created, %i errors" % (self.count, self.errors)

    def handle_label(self, path, **options):

        with open(path, 'r') as data:
            for row in csv.reader(data, delimiter='\t'):
                try:
                    user, password = self.create_user(*row)
                    if self.notify:
                        self.notify_user(user, password)
                except Exception as e:
                    print "Could not create user with values:\n\t%s\n\tError: %s" % ("\t".join(row), str(e))
                    self.errors += 1
                    connection._rollback()
                    continue
