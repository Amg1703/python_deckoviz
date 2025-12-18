from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Background(models.Model):
    """Model for storing generated or uploaded background images"""
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    SERVICE_CHOICES = [
        ('runware', 'Runware'),
        ('user_uploaded', 'User Uploaded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='poster_backgrounds')
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    image_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # Image metadata
    prompt = models.TextField(help_text="Generation prompt used")
    width = models.IntegerField(default=1024, validators=[MinValueValidator(256), MaxValueValidator(2048)])
    height = models.IntegerField(default=1024, validators=[MinValueValidator(256), MaxValueValidator(2048)])
    style_preset = models.CharField(max_length=100, default='cinematic')
    
    # URLs
    s3_url = models.URLField(null=True, blank=True, help_text="S3 URL if uploaded")
    s3_key = models.CharField(max_length=500, null=True, blank=True, help_text="S3 bucket key")
    local_url = models.URLField(help_text="Local URL fallback")
    
    # Service info
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, default='runware')
    model = models.CharField(max_length=100, null=True, blank=True, help_text="AI model used")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', db_index=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(null=True, blank=True, help_text="Additional metadata")
    is_public = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Background {self.image_uuid} - {self.user.username}"
    
    def get_url(self):
        """Return S3 URL if available, otherwise local URL"""
        return self.s3_url or self.local_url


class QuotePoster(models.Model):
    """Model for storing generated quote posters"""
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    ALIGNMENT_CHOICES = [
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ]
    
    ORIENTATION_CHOICES = [
        ('horizontal', 'Horizontal'),
        ('vertical', 'Vertical'),
        ('square', 'Square'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quote_posters')
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    background = models.ForeignKey(Background, on_delete=models.CASCADE, related_name='posters')
    
    # Quote text
    quote_text = models.TextField(help_text="Quote text displayed on poster")
    
    # Text styling
    font_family = models.CharField(max_length=100, default='arial')
    font_size = models.IntegerField(default=60, validators=[MinValueValidator(20), MaxValueValidator(200)])
    font_color = models.CharField(max_length=7, default='#FFFFFF', help_text="Hex color code")
    alignment = models.CharField(max_length=10, choices=ALIGNMENT_CHOICES, default='center')
    orientation = models.CharField(max_length=15, choices=ORIENTATION_CHOICES, default='horizontal')
    opacity = models.FloatField(default=1.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    shadow = models.BooleanField(default=True, help_text="Add shadow to text")
    
    # URLs
    s3_url = models.URLField(null=True, blank=True, help_text="S3 URL if uploaded")
    s3_key = models.CharField(max_length=500, null=True, blank=True, help_text="S3 bucket key")
    local_url = models.URLField(help_text="Local URL fallback")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', db_index=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(null=True, blank=True, help_text="Additional metadata")
    is_public = models.BooleanField(default=False)
    share_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['session_id']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"Poster {self.session_id} - {self.user.username}"
    
    def get_url(self):
        """Return S3 URL if available, otherwise local URL"""
        return self.s3_url or self.local_url
    
    def increment_share_count(self):
        """Increment share count"""
        self.share_count += 1
        self.save(update_fields=['share_count'])


class PosterFeedback(models.Model):
    """Model for storing user feedback on posters"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poster = models.ForeignKey(QuotePoster, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating 1-5"
    )
    comment = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('poster', 'user')
        indexes = [
            models.Index(fields=['poster']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Feedback for {self.poster.session_id} by {self.user.username}"


class PosterShare(models.Model):
    """Model for tracking shared posters"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poster = models.ForeignKey(QuotePoster, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    share_url = models.URLField(unique=True, db_index=True)
    share_token = models.CharField(max_length=100, unique=True, db_index=True)
    
    view_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['share_token']),
            models.Index(fields=['poster']),
        ]
    
    def __str__(self):
        return f"Share of {self.poster.session_id}"
    
    def is_expired(self):
        """Check if share link has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])