from django.db import models
import uuid


class NarrationStatusEnum(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING_IMAGES = "processing_images", "Processing Images"
    PROCESSING_VIDEO = "processing_video", "Processing Video"
    GENERATING_SCRIPT = "generating_script", "Generating Script"
    GENERATING_VOICE = "generating_voice", "Generating Voice"
    CREATING_VIDEO = "creating_video", "Creating Video"
    ADDING_AUDIO = "adding_audio", "Adding Audio"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class InputTypeEnum(models.TextChoices):
    IMAGES = "images", "Images"
    VIDEO = "video", "Video"


class CollectionNarration(models.Model):
    """Collection with Narration model"""
    
    narration_id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, db_index=True)
    product_name = models.CharField(max_length=500)
    product_description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=NarrationStatusEnum.choices,
        default=NarrationStatusEnum.PENDING
    )
    input_type = models.CharField(
        max_length=20,
        choices=InputTypeEnum.choices,
        default=InputTypeEnum.IMAGES
    )
    
    script = models.TextField(null=True, blank=True)
    audio_path = models.CharField(max_length=500, null=True, blank=True)
    video_path = models.CharField(max_length=500, null=True, blank=True)
    final_video_path = models.CharField(max_length=500, null=True, blank=True)
    
    audio_duration = models.FloatField(null=True, blank=True)
    video_duration = models.FloatField(null=True, blank=True)
    
    download_url = models.CharField(max_length=500, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "collection_narrations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"{self.product_name} ({self.narration_id})"
