from django.db import models

class Follower(models.Model):
    
    name = models.CharField( max_length=255 )
    email = models.EmailField( unique=True )
    added = models.DateTimeField( auto_now=True )

    def __unicode__(self):
        return "%s <%s>" % (self.name, self.email)

    class Meta:
        db_table = 'followers'
        ordering = ['added', 'name']
        get_latest_by = 'added'
