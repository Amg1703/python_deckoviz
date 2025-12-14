from django.contrib import admin
from .models import MusicTask, Lyrics, MusicVideo


@admin.register(MusicTask)
class MusicTaskAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'user_id', 'type', 'status', 'style', 'created_at')
    list_filter = ('status', 'type', 'instrumental', 'created_at')
    search_fields = ('request_id', 'user_id', 'task_id', 'prompt')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Identification', {
            'fields': ('request_id', 'task_id', 'user_id')
        }),
        ('Task Details', {
            'fields': ('type', 'lyrics_id', 'status', 'prompt', 'style', 
                      'vocal_gender', 'instrumental', 'model')
        }),
        ('Results', {
            'fields': ('songs', 'progress', 'error')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Lyrics)
class LyricsAdmin(admin.ModelAdmin):
    list_display = ('lyrics_id', 'user_id', 'prompt', 'music_generated', 'status', 'created_at')
    list_filter = ('status', 'music_generated', 'created_at')
    search_fields = ('lyrics_id', 'user_id', 'prompt', 'lyrics')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Identification', {
            'fields': ('lyrics_id', 'user_id')
        }),
        ('Content', {
            'fields': ('prompt', 'lyrics', 'status')
        }),
        ('Music Generation', {
            'fields': ('music_generated', 'music_request_id')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(MusicVideo)
class MusicVideoAdmin(admin.ModelAdmin):
    list_display = ('video_id', 'user_id', 'status', 'author', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('video_id', 'user_id', 'request_id', 'task_id', 'audio_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Identification', {
            'fields': ('video_id', 'user_id')
        }),
        ('References', {
            'fields': ('request_id', 'task_id', 'audio_id')
        }),
        ('Video Details', {
            'fields': ('author', 'domain_name', 'status', 'video_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
