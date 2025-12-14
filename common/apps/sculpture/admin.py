from django.contrib import admin
from .models import Sculpture, SculptureImage


@admin.register(Sculpture)
class SculptureAdmin(admin.ModelAdmin):
    list_display = ["job_id", "user", "status", "created_at"]
    search_fields = ["job_id", "user__username", "title"]
    list_filter = ["status", "created_at", "is_shared"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(SculptureImage)
class SculptureImageAdmin(admin.ModelAdmin):
    list_display = ["filename", "job_id", "sculpture", "angle_number", "created_at"]
    search_fields = ["filename", "job_id"]
    readonly_fields = ["created_at", "updated_at"]