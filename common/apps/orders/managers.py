from django.db import models 

class OrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(is_active=True)

    def for_user(self, user):
        return self.get_queryset().filter(user=user,is_active=True)