from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import BaseModel

User = get_user_model()


class Sculpture(BaseModel):
    """Main sculpture record"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sculptures")
    job_id = models.CharField(max_length=128, unique=True, db_index=True)
    
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # File paths
    input_filename = models.CharField(max_length=500, blank=True, null=True)
    output_filename = models.CharField(max_length=500, blank=True, null=True)

    # Generation details
    prompt = models.TextField(blank=True, null=True)
    style = models.CharField(max_length=255, blank=True, null=True)

    # Processing
    status = models.CharField(
        max_length=50, 
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ]
    )
    service = models.CharField(max_length=64, default="runware")
    model = models.CharField(max_length=128, default="google:4@1")

    # S3 URLs
    s3_url = models.URLField(max_length=2000, blank=True, null=True)
    s3_key = models.CharField(max_length=1000, blank=True, null=True)

    # Sharing & feedback
    is_shared = models.BooleanField(default=False)
    share = models.BooleanField(default=False)
    
    # Feedback
    rating = models.IntegerField(null=True, blank=True, choices=[(i, str(i)) for i in range(1, 6)])
    feedback_comment = models.TextField(blank=True, null=True)
    feedback_submitted_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["job_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Sculpture {self.job_id} - {self.user.username}"


class SculptureImage(BaseModel):
    """Individual generated images / angles for a sculpture"""
    sculpture = models.ForeignKey(Sculpture, on_delete=models.CASCADE, related_name="images", null=True, blank=True)
    job_id = models.CharField(max_length=128, db_index=True)
    
    filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000, blank=True, null=True)
    url = models.URLField(max_length=2000, blank=True, null=True)
    s3_key = models.CharField(max_length=1000, blank=True, null=True)
    
    # Image metadata
    mime_type = models.CharField(max_length=50, default="image/png")
    file_size = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    # Angle tracking
    angle_number = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["angle_number", "created_at"]
        indexes = [
            models.Index(fields=["job_id"]),
            models.Index(fields=["sculpture", "angle_number"]),
        ]

    def __str__(self):
        if self.angle_number:
            return f"{self.filename} - Angle {self.angle_number}"
        return f"{self.filename} ({self.job_id})"