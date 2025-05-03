from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from apps.utils.choices import ADDRESS_TYPES
from .managers import AddressManager

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
    room = models.UUIDField(default=uuid.uuid4, blank=False, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email', 'username', 'first_name', 'last_name', 'is_active', 'room']),
        ]
        
class Address(BaseModel):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=255, choices=ADDRESS_TYPES, default='billing')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}, {self.country}, {self.zip_code}"
    
    objects = AddressManager()
    class Meta:
        db_table = 'addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        indexes = [
            models.Index(fields=['user']),
        ]