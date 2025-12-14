from django.contrib import admin
from .models import BeforeAfter

@admin.register(BeforeAfter)
class BeforeAfterAdmin(admin.ModelAdmin):
    list_display = ("job_id", "user_id", "transformation_type", "status", "created_at")
    search_fields = ("job_id", "user_id", "before_filename", "after_filename")
    readonly_fields = ("created_at", "updated_at")
