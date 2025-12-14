from django.contrib import admin
from .models import DeckovizComparison

@admin.register(DeckovizComparison)
class DeckovizComparisonAdmin(admin.ModelAdmin):
    list_display = ("job_id", "user_id", "deckoviz_variant", "size", "status", "created_at")
    search_fields = ("job_id", "user_id", "before_filename", "after_filename")
    readonly_fields = ("created_at", "updated_at")