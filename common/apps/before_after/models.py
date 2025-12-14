from django.conf import settings
from django.db import models


class BeforeAfter(models.Model):
    TRANSFORM_CHOICES = [
        ("deckoviz", "Deckoviz"),
        ("general_edit", "General Edit"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    job_id = models.CharField(max_length=128, unique=True)
    before_filename = models.CharField(max_length=1024, blank=True)
    after_filename = models.CharField(max_length=1024, blank=True)
    transformation_type = models.CharField(max_length=64, choices=TRANSFORM_CHOICES, default="general_edit")

    prompt = models.TextField(blank=True, null=True)
    edit_instructions = models.TextField(blank=True, null=True)
    style_hint = models.CharField(max_length=128, blank=True, null=True)

    s3_before_url = models.CharField(max_length=2048, blank=True, null=True)
    s3_before_key = models.CharField(max_length=2048, blank=True, null=True)
    s3_after_url = models.CharField(max_length=2048, blank=True, null=True)
    s3_after_key = models.CharField(max_length=2048, blank=True, null=True)

    status = models.CharField(max_length=64, default="pending")
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_id} ({self.transformation_type})"