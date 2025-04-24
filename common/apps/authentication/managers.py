from django.db import models 


class AddressManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
    def for_user(self, user):
        return self.get_queryset().filter(user=user)
    
