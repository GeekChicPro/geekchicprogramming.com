from django.db import models
from django.contrib.auth.models import User
from geekchic.utils.cast import boolean
from notify import send_feedback

class Feedback(models.Model):
    """
    @note: Not currently used in geekchicprogramming.com
    """

    CATEGORIES = (
        ('I', 'Information'),
        ('R', 'Request'),
        ('C', 'Problem'),
        ('F', 'Feedback'),
        ('Q', 'Question'),
        ('O', 'Anything Else'),
    )

    name      = models.CharField( max_length=50 )
    email     = models.EmailField( )
    comment   = models.TextField( )
    category  = models.CharField( max_length=1, choices=CATEGORIES, default='O' )
    reply     = models.BooleanField( default=True )
    timestamp = models.DateTimeField( auto_now_add=True )

    class Meta:
        db_table = "feedback"
        get_latest_by = 'timestamp'

    def save(self):
        send_feedback(self)
        super(Feedback, self).save()

    def __unicode__(self):
        return self.comment

    def __str__(self):
        return self.comment
