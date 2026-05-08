from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    F-02: Automatically create a UserProfile when a new User is registered.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
