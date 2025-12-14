from django.contrib import admin
from .models import VisualAudiobook

@admin.register(VisualAudiobook)
class VisualAudiobookAdmin(admin.ModelAdmin):
    """Admin interface for Visual Audiobook"""
    
    list_display = [
        'book_title', 'user', 'voice', 'art_style', 'num_frames',
        'status', 'video_size_mb', 'created_at', 'completed_at'
    ]
    
    list_filter = ['status', 'voice', 'art_style', 'created_at']
    
    search_fields = ['book_title', 'user__username', 'user__email']
    
    readonly_fields = [
        'id', 'video_url', 'video_duration', 'video_size_mb',
        'text_extracted', 'num_pages', 'error_message',
        'created_at', 'updated_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Audiobook Info', {
            'fields': ('id', 'user', 'book_title')
        }),
        ('Processing Settings', {
            'fields': ('voice', 'art_style', 'num_frames')
        }),
        ('Input', {
            'fields': ('pdf_file_url', 'text_extracted', 'num_pages')
        }),
        ('Output', {
            'fields': ('video_url', 'video_duration', 'video_size_mb')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation from admin (only via API)"""
        return False