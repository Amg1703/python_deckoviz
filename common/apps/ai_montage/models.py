from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import BaseModel

User = get_user_model()


class MontageStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SELECTING_IMAGES = "selecting_images", "Selecting Images"
    SEARCHING_MUSIC = "searching_music", "Searching Music"
    DOWNLOADING_MUSIC = "downloading_music", "Downloading Music"
    CREATING_VIDEO = "creating_video", "Creating Video"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class UploadedImage(BaseModel):
    """Images uploaded by user for montage creation"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='montage_images')
    montage = models.ForeignKey('Montage', on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_images')
    
    filename = models.CharField(max_length=500)
    original_filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000)
    file_size = models.IntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=1000)
    thumbnail_url = models.CharField(max_length=1000, null=True, blank=True)
    
    class Meta:
        db_table = 'ai_montage_uploaded_images'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_filename} ({self.user.username})"


class Montage(BaseModel):
    """AI-generated video montages from user images with music"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='montages')
    
    # User input
    prompt = models.CharField(max_length=500)
    mood = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=MontageStatus.choices,
        default=MontageStatus.PENDING,
        db_index=True
    )
    
    # Parsed details
    theme = models.CharField(max_length=255, null=True, blank=True)
    music_style = models.CharField(max_length=255, null=True, blank=True)
    music_tags = models.JSONField(null=True, blank=True)
    
    # Selected resources
    selected_image_paths = models.JSONField(null=True, blank=True)
    music_url = models.CharField(max_length=500, null=True, blank=True)
    music_title = models.CharField(max_length=255, null=True, blank=True)
    music_artist = models.CharField(max_length=255, null=True, blank=True)
    music_license = models.CharField(max_length=500, null=True, blank=True)
    music_attribution = models.TextField(null=True, blank=True)
    
    # Output
    video_path = models.CharField(max_length=500, null=True, blank=True)
    video_duration = models.FloatField(null=True, blank=True)
    thumbnail_path = models.CharField(max_length=500, null=True, blank=True)
    output_video_url = models.CharField(max_length=500, null=True, blank=True)
    
    # Metadata
    total_images_uploaded = models.IntegerField(default=0)
    images_used = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_montages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Montage {self.id} - {self.user.username} ({self.status})"
