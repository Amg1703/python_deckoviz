from django.contrib import admin
from .models import CollectionNarration


@admin.register(CollectionNarration)
class CollectionNarrationAdmin(admin.ModelAdmin):
    list_display = [
        'narration_id',
        'user_id',
        'product_name',
        'status',
        'input_type',
        'created_at',
        'updated_at',
    ]
    list_filter = ['status', 'input_type', 'created_at']
    search_fields = ['narration_id', 'user_id', 'product_name']
    readonly_fields = ['narration_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('narration_id', 'user_id', 'product_name', 'product_description')
        }),
        ('Status', {
            'fields': ('status', 'input_type', 'error_message')
        }),
        ('Media Paths', {
            'fields': ('audio_path', 'video_path', 'final_video_path', 'download_url')
        }),
        ('Content', {
            'fields': ('script',)
        }),
        ('Durations', {
            'fields': ('audio_duration', 'video_duration')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
