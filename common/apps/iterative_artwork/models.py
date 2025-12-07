from django.db import models
from django.contrib.postgres.fields import ArrayField


class IterativeArtwork(models.Model):
    """Iterative Artwork model for saved artworks"""
    
    user_id = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=500)
    final_image_url = models.TextField()
    final_image_path = models.TextField(null=True, blank=True)
    final_prompt = models.TextField()
    conversation_history = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "iterative_artworks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.user_id}"


class IterativeArtworkIteration(models.Model):
    """Iteration model for artwork creation process"""
    
    artwork = models.ForeignKey(
        IterativeArtwork,
        on_delete=models.CASCADE,
        related_name='iterations',
        null=True,
        blank=True
    )
    user_id = models.CharField(max_length=255, db_index=True)
    user_prompt = models.TextField()
    assistant_response = models.TextField()
    reference_image_path = models.TextField(null=True, blank=True)
    generated_image_url = models.TextField(null=True, blank=True)
    generated_image_path = models.TextField(null=True, blank=True)
    image_prompt = models.TextField(null=True, blank=True)
    iteration_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "iterative_artwork_iterations"
        ordering = ["iteration_number"]
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["artwork_id"]),
            models.Index(fields=["iteration_number"]),
        ]
    
    def __str__(self):
        return f"Iteration {self.iteration_number} for {self.user_id}"
