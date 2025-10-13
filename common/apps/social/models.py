from django.db import models
from django.conf import settings
from apps.authentication.models import BaseModel

INTERACTION_TYPES = [
    ("like", "Like"),
    ("share", "Share"),
]

class SocialConnection(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_connections")
    connection = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="connected_to")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "connection")

class ImageInteraction(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ForeignKey('gallery.Image', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

class CollectionInteraction(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    collection = models.ForeignKey('gallery.Collection', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
