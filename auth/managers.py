__author__ = 'benjamin'

from django.db import models
from auth.utils import generate_password

class StudentManager(models.Manager):

    def unique_username(self, username, depth=0):
        """
        Checks if the username is unique in the database,
        if not, it appends a stringified integer to the end and
        tries again, called recursively.
        """
        taken = bool(self.filter(username=username).count())
        if taken:
            depth += 1
            if depth > 1:
                dpstr = str(depth-1)
                username = username[:-len(dpstr)] + str(depth)
            else:
                username += str(depth)
            return self.unique_username(username, depth)
        return username

    def create_with_username(self, **kwargs):

        password   = kwargs.pop('password', None) or generate_password()

        first_name = kwargs.get('first_name', '')
        last_name  = kwargs.get('last_name', '')

        if not last_name:
            raise ValueError("Must supply at least last name with this method.")

        username = first_name[0] + last_name if first_name else last_name
        username = username.lower()
        username = kwargs.pop('username', username)

        # Check for uniqueness of username:
        username = self.unique_username(username)

        # Create the user with the new values
        kwargs['username'] = username
        student  = self.create(**kwargs)

        # Set the password on the model
        student.set_password(password)
        student.save()

        return student

    def unique_emails(self):
        """
        Returns a dictionary of User values that have unique email
        addresses since this is not a property of the normal contrib model
        """
        return self.values('email', 'first_name', 'last_name').distinct()
