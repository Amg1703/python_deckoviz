from django.db import models
from django.utils import timezone
from datetime import timedelta

class SocialConnectionManager(models.Manager):
    def friends_of(self, user):
        return self.filter(user=user)

class ImageInteractionManager(models.Manager):
    def likes(self):
        return self.filter(interaction_type='like')
    def recent(self):
        return self.filter(created_at__gte=timezone.now() - timedelta(days=1))

class CollectionInteractionManager(models.Manager):
    def likes(self):
        return self.filter(interaction_type='like')
    def recent(self):
        return self.filter(created_at__gte=timezone.now() - timedelta(days=1))
