from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import BaseModel
from apps.gallery.models import Image

User = get_user_model()

class StyleOption(BaseModel):
    """Style options for AI style transfer"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='style_thumbnails/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class StyledImage(BaseModel):
    """Images created through AI style transfer"""
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='styled_versions')
    style = models.ForeignKey(StyleOption, on_delete=models.SET_NULL, null=True, related_name='styled_images')
    result_image = models.ImageField(upload_to='styled_images/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='styled_images')
    
    class Meta:
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['original_image']),
        ]
    
    def __str__(self):
        return f"{self.original_image} styled with {self.style.name if self.style else 'custom style'}"

class AIGeneratedImage(BaseModel):
    """Images created through AI generation from text prompts"""
    prompt = models.TextField()
    result_image = models.ImageField(upload_to='ai_generated/')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_generated_images')
    
    class Meta:
        indexes = [
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"AI generated image from prompt: {self.prompt[:30]}..."
