from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import BaseModel

User = get_user_model()

class SequentialArtwork(BaseModel):
    """Store sequential artwork sequences"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sequential_artworks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    total_iterations = models.IntegerField(default=0)
    
    # JSON field to store sequence of image URLs
    sequence_images = models.JSONField(default=list, help_text="List of image URLs in sequence order")
    s3_image_keys = models.JSONField(default=list, help_text="List of S3 keys for each image")
    
    first_image_url = models.URLField(max_length=1000, blank=True, null=True)
    last_image_url = models.URLField(max_length=1000, blank=True, null=True)
    
    # Metadata
    conversation_history = models.JSONField(default=dict, help_text="Chat conversation history")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class SequentialArtworkIteration(BaseModel):
    """Store individual iterations of a sequence"""
    artwork = models.ForeignKey(SequentialArtwork, on_delete=models.CASCADE, related_name='iterations', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artwork_iterations')
    
    iteration_number = models.IntegerField()
    user_prompt = models.TextField()
    assistant_response = models.TextField()
    image_prompt = models.TextField(blank=True, null=True)
    
    reference_image_path = models.CharField(max_length=500, blank=True, null=True)
    generated_image_url = models.URLField(max_length=1000, blank=True, null=True)  # Add null=True
    generated_image_path = models.CharField(max_length=500, blank=True, null=True)
    
    s3_image_url = models.URLField(max_length=1000, blank=True, null=True)
    s3_image_key = models.CharField(max_length=1000, blank=True, null=True)
    
    is_saved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['iteration_number']
        unique_together = ['artwork', 'iteration_number']
        indexes = [
            models.Index(fields=['user', 'is_saved']),
            models.Index(fields=['artwork', 'iteration_number']),
        ]
    
    def __str__(self):
        if self.artwork:
            return f"{self.artwork.title} - Iteration {self.iteration_number}"
        return f"Unsaved Iteration {self.iteration_number}"