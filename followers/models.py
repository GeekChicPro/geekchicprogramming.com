from django.db import models

class Follower(models.Model):
    
    name = models.CharField( max_length=255 )
    email = models.EmailField( unique=True )
    added = models.DateTimeField( auto_now=True )

    class Meta:
        db_table = 'followers'
        ordering = ['added', 'name']
        get_latest_by = 'added'
