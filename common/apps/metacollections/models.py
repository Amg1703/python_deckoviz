from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import BaseModel
from apps.gallery.models import Collection

User = get_user_model()

class MetaCollection(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='meta_collection')
    favourite_collections = models.ManyToManyField(Collection, related_name='favourited_by_meta_collections', blank=True)

    class Meta:
        db_table = 'meta_collections'
        verbose_name = 'Meta Collection'
        verbose_name_plural = 'Meta Collections'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username}'s Meta Collection" 