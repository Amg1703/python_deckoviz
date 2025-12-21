from django.contrib import admin
from .models import SequentialArtwork, SequentialArtworkIteration

@admin.register(SequentialArtwork)
class SequentialArtworkAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'total_iterations', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Sequence Data', {
            'fields': ('total_iterations', 'sequence_images', 's3_image_keys', 'first_image_url', 'last_image_url')
        }),
        ('Metadata', {
            'fields': ('conversation_history',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SequentialArtworkIteration)
class SequentialArtworkIterationAdmin(admin.ModelAdmin):
    list_display = ['artwork', 'iteration_number', 'user', 'is_saved', 'created_at']
    list_filter = ['is_saved', 'created_at', 'user']
    search_fields = ['artwork__title', 'user__username', 'user_prompt']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Artwork & Iteration', {
            'fields': ('artwork', 'user', 'iteration_number', 'is_saved')
        }),
        ('Content', {
            'fields': ('user_prompt', 'assistant_response', 'image_prompt')
        }),
        ('Images', {
            'fields': ('reference_image_path', 'generated_image_url', 'generated_image_path', 's3_image_url', 's3_image_key')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )