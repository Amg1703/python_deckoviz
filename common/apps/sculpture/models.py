from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import BaseModel

User = get_user_model()


class Sculpture(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sculptures")
    job_id = models.CharField(max_length=128, unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    input_filename = models.CharField(max_length=500, blank=True, null=True)
    output_filename = models.CharField(max_length=500, blank=True, null=True)

    prompt = models.TextField(blank=True, null=True)
    style = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=50, default="created")
    is_shared = models.BooleanField(default=False)

    # S3 info
    s3_url = models.URLField(max_length=1000, blank=True, null=True)
    s3_key = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Sculpture {self.job_id} - {self.user.username}"


class SculptureImage(BaseModel):
    """Individual generated images / angles for a sculpture job"""
    sculpture = models.ForeignKey(Sculpture, on_delete=models.CASCADE, related_name="images", null=True, blank=True)
    job_id = models.CharField(max_length=128, db_index=True)
    filename = models.CharField(max_length=500)
    file_path = models.CharField(max_length=1000, blank=True, null=True)
    url = models.URLField(max_length=1000, blank=True, null=True)
    s3_key = models.CharField(max_length=1000, blank=True, null=True)
    mime_type = models.CharField(max_length=50, default="image/png")
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    angle_number = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["job_id"]),
        ]

    def __str__(self):
        return f"{self.filename} ({self.job_id})"