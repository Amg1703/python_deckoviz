from django.contrib import admin
from .models import Sculpture, SculptureImage


@admin.register(Sculpture)
class SculptureAdmin(admin.ModelAdmin):
    list_display = ["job_id", "user", "status", "service", "model", "is_shared", "created_at"]
    search_fields = ["job_id", "user__username", "title"]
    list_filter = ["status", "service", "is_shared", "share", "created_at"]
    readonly_fields = ["created_at", "updated_at", "job_id"]
    
    fieldsets = (
        ("Basic Info", {
            "fields": ("user", "job_id", "title", "description")
        }),
        ("Generation", {
            "fields": ("input_filename", "output_filename", "prompt", "style")
        }),
        ("Processing", {
            "fields": ("status", "service", "model")
        }),
        ("S3 Storage", {
            "fields": ("s3_url", "s3_key"),
            "classes": ("collapse",)
        }),
        ("Sharing & Feedback", {
            "fields": ("is_shared", "share", "rating", "feedback_comment", "feedback_submitted_at")
        }),
        ("Metadata", {
            "fields": ("metadata",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(SculptureImage)
class SculptureImageAdmin(admin.ModelAdmin):
    list_display = ["filename", "job_id", "sculpture", "angle_number", "mime_type", "created_at"]
    search_fields = ["filename", "job_id", "sculpture__job_id"]
    list_filter = ["mime_type", "angle_number", "created_at"]
    readonly_fields = ["created_at", "updated_at", "job_id"]
    
    fieldsets = (
        ("Image Info", {
            "fields": ("sculpture", "job_id", "filename", "angle_number")
        }),
        ("File Details", {
            "fields": ("file_path", "mime_type", "file_size", "width", "height")
        }),
        ("Storage", {
            "fields": ("url", "s3_key"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )