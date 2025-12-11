from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class VisualAudiobook(models.Model):
    """Model for storing visual audiobook records"""
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audiobooks')
    book_title = models.CharField(max_length=255)
    voice = models.CharField(max_length=50)
    art_style = models.CharField(max_length=100)
    num_frames = models.IntegerField()
    
    # PDF info
    pdf_file_url = models.URLField(null=True, blank=True)
    text_extracted = models.TextField(null=True, blank=True)
    num_pages = models.IntegerField(null=True, blank=True)
    
    # Video output
    video_url = models.URLField(null=True, blank=True)
    video_duration = models.FloatField(null=True, blank=True)
    video_size_mb = models.FloatField(null=True, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.book_title} - {self.user.username}"