from django.conf import settings
from django.db import models


class BeforeAfter(models.Model):
    TRANSFORM_CHOICES = [
        ("room_edit", "Room Edit"),
        ("deckoviz_placement", "Deckoviz Placement"),
    ]
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    session_id = models.CharField(max_length=256, unique=True, db_index=True)
    job_id = models.CharField(max_length=128, blank=True, db_index=True)
    
    # Image references
    original_filename = models.CharField(max_length=1024, blank=True)
    original_image_uuid = models.CharField(max_length=256, blank=True)
    edited_filename = models.CharField(max_length=1024, blank=True)
    
    # Edit details
    transformation_type = models.CharField(max_length=64, choices=TRANSFORM_CHOICES, default="room_edit")
    edit_instructions = models.TextField(blank=True, null=True)
    style_hint = models.CharField(max_length=128, blank=True, null=True)
    
    # Deckoviz specific fields
    placement_instructions = models.TextField(blank=True, null=True)
    deckoviz_variant = models.CharField(max_length=64, blank=True, null=True)  # "standard", "wall", "sculpture", "multi-unit"
    size_variant = models.CharField(max_length=64, blank=True, null=True)  # "45", "55", "65", etc.
    halo_color = models.CharField(max_length=128, blank=True, null=True)
    frame_material = models.CharField(max_length=128, blank=True, null=True)
    preserve_room = models.BooleanField(default=True)
    
    # S3 URLs
    s3_original_url = models.CharField(max_length=2048, blank=True, null=True)
    s3_original_key = models.CharField(max_length=2048, blank=True, null=True)
    s3_output_url = models.CharField(max_length=2048, blank=True, null=True)
    s3_output_key = models.CharField(max_length=2048, blank=True, null=True)
    
    # Change log & metadata
    change_log_path = models.CharField(max_length=1024, blank=True, null=True)
    change_log_s3_url = models.CharField(max_length=2048, blank=True, null=True)
    change_log_s3_key = models.CharField(max_length=2048, blank=True, null=True)
    
    metadata_path = models.CharField(max_length=1024, blank=True, null=True)
    metadata_s3_url = models.CharField(max_length=2048, blank=True, null=True)
    metadata_s3_key = models.CharField(max_length=2048, blank=True, null=True)
    
    # Processing details
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default="pending")
    service = models.CharField(max_length=64, default="runware")
    model = models.CharField(max_length=128, default="google:4@1")
    
    # Parsed data
    parsed_changes = models.JSONField(default=dict, blank=True)
    deckoviz_specs = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Sharing & privacy
    share = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["job_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.session_id} ({self.transformation_type})"