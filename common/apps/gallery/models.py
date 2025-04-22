from django.db import models
from apps.authentication.models import BaseModel
from django.contrib.auth import get_user_model
from apps.utils import INTERACTION_TYPES

User = get_user_model()

class Image(BaseModel):
    file = models.ImageField(upload_to='images/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_images')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"Image {self.id}"
    
    
class Collection(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=255)
    display_time = models.IntegerField(default=10, help_text="Time in seconds to display each image")
    music_preference = models.CharField(max_length=255, blank=True)
    meta_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username}'s collection: {self.name}"  
    
class CollectionImage(BaseModel):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection_images')
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='image_collections')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['collection', 'image']
        

class ImageInteraction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_interactions')
    # Support both internal and external images
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='interactions', null=True, blank=True)
    external_image_id = models.CharField(max_length=255, null=True, blank=True)  # For external images
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['image']),
            models.Index(fields=['external_image_id']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'image', 'interaction_type'],
                condition=models.Q(image__isnull=False),
                name='unique_internal_image_interaction'
            ),
            models.UniqueConstraint(
                fields=['user', 'external_image_id', 'interaction_type'],
                condition=models.Q(external_image_id__isnull=False),
                name='unique_external_image_interaction'
            ),
            models.CheckConstraint(
                check=(
                    models.Q(image__isnull=False, external_image_id__isnull=True) | 
                    models.Q(image__isnull=True, external_image_id__isnull=False)
                ),
                name='either_internal_or_external_image'
            )
        ]

    def __str__(self):
        image_identifier = self.image.id if self.image else self.external_image_id
        return f"{self.user.username} - {self.interaction_type} - {image_identifier}"


 
class MetaComment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    # Support both internal and external images
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    external_image_id = models.CharField(max_length=255, null=True, blank=True)  # For external images
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['image']),
            models.Index(fields=['external_image_id']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(image__isnull=False, external_image_id__isnull=True) | 
                    models.Q(image__isnull=True, external_image_id__isnull=False)
                ),
                name='comment_either_internal_or_external_image'
            )
        ]

    def __str__(self):
        image_identifier = self.image.id if self.image else self.external_image_id
        return f"Comment by {self.user.username} on {image_identifier}"