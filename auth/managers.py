__author__ = 'benjamin'

from django.db import models

class StudentManager(models.Manager):

    def unique_emails(self):
        """
        Returns a dictionary of User values that have unique email
        addresses since this is not a property of the normal contrib model
        """
        return self.values('email', 'first_name', 'last_name').distinct()
