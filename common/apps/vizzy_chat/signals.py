"""
Vizzy Chat Django Signals

Signal handlers for automatic actions on model events
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import VizzyUserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_vizzy_profile(sender, instance, created, **kwargs):
    """
    Automatically create VizzyUserProfile when a new user is created
    
    This ensures every user has a Vizzy profile without explicit creation
    """
    if created:
        VizzyUserProfile.objects.get_or_create(user=instance)
