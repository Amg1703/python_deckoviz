from django.conf import settings
from django.db import models


class DeckovizComparison(models.Model):
    """
    Stores Deckoviz-specific before/after comparisons.
    Mirrors functionality of the general before_after app but scoped for Deckoviz installs.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    job_id = models.CharField(max_length=128, unique=True)
    before_filename = models.CharField(max_length=1024, blank=True)
    after_filename = models.CharField(max_length=1024, blank=True)

    deckoviz_variant = models.CharField(max_length=128, blank=True, null=True)
    size = models.CharField(max_length=32, blank=True, null=True)
    halo_color = models.CharField(max_length=64, blank=True, null=True)
    content_type = models.CharField(max_length=128, blank=True, null=True)
    placement_instructions = models.TextField(blank=True, null=True)

    s3_before_url = models.CharField(max_length=2048, blank=True, null=True)
    s3_before_key = models.CharField(max_length=2048, blank=True, null=True)
    s3_after_url = models.CharField(max_length=2048, blank=True, null=True)
    s3_after_key = models.CharField(max_length=2048, blank=True, null=True)

    prompt = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=64, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_id} (Deckoviz)"