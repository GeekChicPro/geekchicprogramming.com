
def create_profile(sender, instance, signal, created, **kwargs):
    """
    When a user is created, also create a matching profile.
    """

    from auth.models import StudentProfile

    if created:
        StudentProfile(user=instance).save()
