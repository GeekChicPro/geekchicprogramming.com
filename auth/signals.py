
def create_profile(sender, instance, signal, created, **kwargs):
    """
    When a user is created, also create a matching profile.
    """

    from auth.models import UserProfile

    if created:
        UserProfile(user=instance).save()
