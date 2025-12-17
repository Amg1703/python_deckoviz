from django.contrib import admin
from .models import BeforeAfter


@admin.register(BeforeAfter)
class BeforeAfterAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "user_id",
        "transformation_type",
        "status",
        "service",
        "created_at"
    )
    list_filter = ("transformation_type", "status", "service", "created_at")
    search_fields = ("session_id", "job_id", "user__username", "user__id")
    readonly_fields = ("created_at", "updated_at", "id")
    
    fieldsets = (
        ("Basic Info", {
            "fields": ("user", "session_id", "job_id", "status", "created_at", "updated_at")
        }),
        ("Transformation Details", {
            "fields": (
                "transformation_type",
                "edit_instructions",
                "style_hint",
                "placement_instructions",
            )
        }),
        ("Deckoviz Specs", {
            "fields": (
                "deckoviz_variant",
                "size_variant",
                "halo_color",
                "frame_material",
                "preserve_room",
                "deckoviz_specs",
            ),
            "classes": ("collapse",)
        }),
        ("Image Files", {
            "fields": (
                "original_filename",
                "original_image_uuid",
                "edited_filename",
            )
        }),
        ("S3 URLs", {
            "fields": (
                "s3_original_url",
                "s3_original_key",
                "s3_output_url",
                "s3_output_key",
            ),
            "classes": ("collapse",)
        }),
        ("Logs & Metadata", {
            "fields": (
                "change_log_path",
                "change_log_s3_url",
                "change_log_s3_key",
                "metadata_path",
                "metadata_s3_url",
                "metadata_s3_key",
            ),
            "classes": ("collapse",)
        }),
        ("Processing", {
            "fields": ("service", "model", "share"),
            "classes": ("collapse",)
        }),
        ("Parsed Data", {
            "fields": ("parsed_changes", "metadata"),
            "classes": ("collapse",)
        }),
    )