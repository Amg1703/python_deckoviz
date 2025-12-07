from django.db import models
from django.utils import timezone


class MusicTask(models.Model):
    """Music generation task tracking"""
    
    TYPE_CHOICES = [
        ('music', 'Music'),
        ('lyrics_to_music', 'Lyrics to Music'),
    ]
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('error', 'Error'),
    ]
    
    request_id = models.CharField(max_length=100, unique=True, db_index=True)
    task_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    lyrics_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='processing')
    prompt = models.TextField(null=True, blank=True)
    style = models.CharField(max_length=100, null=True, blank=True)
    vocal_gender = models.CharField(max_length=10, null=True, blank=True)
    instrumental = models.BooleanField(default=False)
    model = models.CharField(max_length=50, null=True, blank=True)
    songs = models.JSONField(null=True, blank=True)
    progress = models.CharField(max_length=255, null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'music_tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['request_id']),
        ]
    
    def __str__(self):
        return f"MusicTask {self.request_id} - {self.status}"


class Lyrics(models.Model):
    """Generated lyrics"""
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    lyrics_id = models.CharField(max_length=100, unique=True, db_index=True)
    user_id = models.CharField(max_length=100, db_index=True)
    prompt = models.TextField()
    lyrics = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='completed')
    music_generated = models.BooleanField(default=False)
    music_request_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'lyrics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['lyrics_id']),
        ]
    
    def __str__(self):
        return f"Lyrics {self.lyrics_id}"


class MusicVideo(models.Model):
    """Music video generation tracking"""
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    video_id = models.CharField(max_length=100, unique=True, db_index=True)
    user_id = models.CharField(max_length=100, db_index=True)
    request_id = models.CharField(max_length=100)
    task_id = models.CharField(max_length=100)
    audio_id = models.CharField(max_length=100)
    author = models.CharField(max_length=255, null=True, blank=True)
    domain_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='processing')
    video_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'music_videos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['video_id']),
        ]
    
    def __str__(self):
        return f"MusicVideo {self.video_id} - {self.status}"
