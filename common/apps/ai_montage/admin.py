from django.contrib import admin
from .models import Montage, UploadedImage


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'original_filename', 'montage', 'created_at']
    list_filter = ['created_at', 'mime_type']
    search_fields = ['user__username', 'user__email', 'original_filename', 'filename']
    raw_id_fields = ['user', 'montage']
    readonly_fields = ['created_at']


@admin.register(Montage)
class MontageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'prompt', 'images_used', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'prompt', 'theme']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'prompt', 'mood', 'status')
        }),
        ('Parsed Details', {
            'fields': ('theme', 'music_style', 'music_tags')
        }),
        ('Resources', {
            'fields': ('selected_image_paths', 'music_url', 'music_title', 'music_artist', 'music_license', 'music_attribution')
        }),
        ('Output', {
            'fields': ('video_path', 'video_duration', 'thumbnail_path', 'output_video_url')
        }),
        ('Metadata', {
            'fields': ('total_images_uploaded', 'images_used', 'error_message', 'created_at', 'updated_at')
        }),
    )
