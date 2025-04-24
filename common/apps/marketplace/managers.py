from django.db import models
from django.db.models import Q

class PriceManager(models.Manager):
    """Manager for active prices"""
    
    def get_queryset(self):
        # full set
        return super().get_queryset()
    
    def active(self):
        # just the active ones
        return self.get_queryset().filter(is_active=True)