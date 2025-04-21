from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseModel(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class User(AbstractUser,BaseModel):
    email = models.EmailField(unique=True)
    profile_visible = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    banner_pictures = models.JSONField(default=list, blank=True)
    bio = models.TextField(validators=[MaxLengthValidator(500)], blank=True) 
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.username