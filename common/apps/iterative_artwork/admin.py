from django.contrib import admin
from .models import IterativeArtwork, IterativeArtworkIteration


class IterativeArtworkIterationInline(admin.TabularInline):
    model = IterativeArtworkIteration
    extra = 0
    readonly_fields = ['created_at']
    fields = ['iteration_number', 'user_prompt', 'generated_image_url', 'created_at']


@admin.register(IterativeArtwork)
class IterativeArtworkAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_id',
        'title',
        'created_at',
        'updated_at',
        'get_iteration_count',
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user_id', 'title', 'final_prompt']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [IterativeArtworkIterationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'title')
        }),
        ('Final Output', {
            'fields': ('final_image_url', 'final_image_path', 'final_prompt')
        }),
        ('Conversation', {
            'fields': ('conversation_history',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_iteration_count(self, obj):
        return obj.iterations.count()
    get_iteration_count.short_description = 'Iterations'


@admin.register(IterativeArtworkIteration)
class IterativeArtworkIterationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_id',
        'artwork_id',
        'iteration_number',
        'created_at',
    ]
    list_filter = ['created_at', 'artwork_id']
    search_fields = ['user_id', 'user_prompt', 'image_prompt']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'artwork', 'iteration_number')
        }),
        ('Prompts', {
            'fields': ('user_prompt', 'assistant_response', 'image_prompt')
        }),
        ('Images', {
            'fields': ('reference_image_path', 'generated_image_url', 'generated_image_path')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
