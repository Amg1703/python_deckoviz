from django.contrib import admin
from .models import Background, QuotePoster, PosterFeedback, PosterShare


@admin.register(Background)
class BackgroundAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'status', 'service', 'width', 'height', 'created_at']
    list_filter = ['status', 'service', 'created_at', 'is_public']
    search_fields = ['user__username', 'prompt', 'session_id']
    readonly_fields = ['id', 'image_uuid', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'session_id', 'image_uuid', 'status')
        }),
        ('Image Details', {
            'fields': ('prompt', 'width', 'height', 'style_preset', 'service', 'model')
        }),
        ('URLs', {
            'fields': ('s3_url', 's3_key', 'local_url')
        }),
        ('Additional', {
            'fields': ('error_message', 'metadata', 'is_public', 'created_at', 'updated_at')
        }),
    )


@admin.register(QuotePoster)
class QuotePosterAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'status', 'font_size', 'share_count', 'created_at']
    list_filter = ['status', 'created_at', 'is_public', 'alignment', 'orientation']
    search_fields = ['user__username', 'quote_text', 'session_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'session_id', 'background', 'status')
        }),
        ('Quote Text', {
            'fields': ('quote_text',)
        }),
        ('Text Styling', {
            'fields': ('font_family', 'font_size', 'font_color', 'alignment', 'orientation', 'opacity', 'shadow')
        }),
        ('URLs', {
            'fields': ('s3_url', 's3_key', 'local_url')
        }),
        ('Sharing & Metrics', {
            'fields': ('is_public', 'share_count')
        }),
        ('Additional', {
            'fields': ('error_message', 'metadata', 'created_at', 'updated_at')
        }),
    )


@admin.register(PosterFeedback)
class PosterFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'poster', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'poster__session_id', 'comment']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Information', {
            'fields': ('id', 'poster', 'user')
        }),
        ('Feedback', {
            'fields': ('rating', 'comment')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


@admin.register(PosterShare)
class PosterShareAdmin(admin.ModelAdmin):
    list_display = ['id', 'poster', 'shared_by', 'is_active', 'view_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['shared_by__username', 'poster__session_id', 'share_token']
    readonly_fields = ['id', 'share_token', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Information', {
            'fields': ('id', 'poster', 'shared_by')
        }),
        ('Share Details', {
            'fields': ('share_token', 'share_url', 'is_active', 'expires_at')
        }),
        ('Metrics', {
            'fields': ('view_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )