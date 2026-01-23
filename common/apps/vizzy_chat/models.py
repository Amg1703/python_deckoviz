"""
Vizzy Chat Database Models

Production-ready models with:
- Proper indexing for performance
- Validation logic
- Manager classes for common queries
- Optimized for horizontal scaling
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class VizzyChatSessionManager(models.Manager):
    """Custom manager for VizzyChatSession with optimized queries"""
    
    def active_sessions(self):
        """Get all active sessions"""
        return self.filter(is_active=True)
    
    def user_sessions(self, user, active_only=True):
        """Get sessions for a specific user"""
        qs = self.filter(user=user).select_related('user')
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.order_by('-updated_at')
    
    def with_message_count(self):
        """Annotate sessions with accurate message count"""
        from django.db.models import Count
        return self.annotate(
            actual_message_count=Count('messages')
        )
    
    def close_inactive_sessions(self, hours=24):
        """Close sessions inactive for specified hours"""
        threshold = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(
            is_active=True,
            updated_at__lt=threshold
        ).update(
            is_active=False,
            closed_at=timezone.now()
        )


class VizzyChatSession(models.Model):
    """
    Chat session for Vizzy conversations
    
    Represents a conversation thread between user and Vizzy AI.
    Sessions can be in 'home' or 'enterprise' mode with different capabilities.
    """
    
    MODE_CHOICES = [
        ('home', 'Home Mode'),
        ('enterprise', 'Enterprise Mode'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique session identifier"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vizzy_sessions',
        help_text="Session owner"
    )
    
    # Session metadata
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional session title (auto-generated or user-set)"
    )
    mode = models.CharField(
        max_length=50,
        choices=MODE_CHOICES,
        default='home',
        help_text="Chat mode: home (casual) or enterprise (professional)"
    )
    
    # State tracking
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether session is currently active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Session creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Session closure timestamp"
    )
    
    # Context tracking
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of last message in session"
    )
    message_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cached count of messages in session"
    )
    
    # Custom manager
    objects = VizzyChatSessionManager()
    
    class Meta:
        db_table = 'vizzy_chat_sessions'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='vizzy_sess_user_created_idx'),
            models.Index(fields=['is_active', '-updated_at'], name='vizzy_sess_active_updated_idx'),
            models.Index(fields=['-updated_at'], name='vizzy_sess_updated_idx'),
        ]
        verbose_name = 'Vizzy Chat Session'
        verbose_name_plural = 'Vizzy Chat Sessions'
    
    def __str__(self):
        return f"Session {self.id} - {self.user.email} ({self.mode})"
    
    def close(self):
        """Close the session"""
        self.is_active = False
        self.closed_at = timezone.now()
        self.save(update_fields=['is_active', 'closed_at', 'updated_at'])
    
    def update_message_count(self):
        """Update cached message count"""
        self.message_count = self.messages.count()
        self.save(update_fields=['message_count', 'updated_at'])
    
    def get_recent_messages(self, limit=20):
        """Get recent messages for context"""
        return self.messages.order_by('-created_at')[:limit]


class VizzyChatMessageManager(models.Manager):
    """Custom manager for VizzyChatMessage"""
    
    def user_messages(self):
        """Get only user messages"""
        return self.filter(role='user')
    
    def assistant_messages(self):
        """Get only assistant messages"""
        return self.filter(role='assistant')
    
    def with_images(self):
        """Get messages containing images"""
        return self.filter(has_images=True)
    
    def session_history(self, session, limit=50):
        """Get conversation history for a session"""
        return self.filter(session=session).select_related(
            'session', 'session__user'
        ).order_by('created_at')[:limit]


class VizzyChatMessage(models.Model):
    """
    Individual messages in Vizzy conversations
    
    Stores all messages (user, assistant, system) with metadata
    including emotional context, performance metrics, and multimodal content.
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Vizzy'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique message identifier"
    )
    session = models.ForeignKey(
        VizzyChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Parent session"
    )
    
    # Message data
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        db_index=True,
        help_text="Message sender role"
    )
    content = models.TextField(
        help_text="Message content (text)"
    )
    
    # Multimodal support
    has_images = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether message includes images"
    )
    image_urls = models.JSONField(
        null=True,
        blank=True,
        default=list,
        help_text="List of S3 URLs for images (if any)"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Message creation timestamp"
    )
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Number of tokens used in LLM processing"
    )
    processing_time_ms = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Processing time in milliseconds"
    )
    
    # Emotional context
    detected_emotion = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Detected emotion label (joy, calm, stress, etc.)"
    )
    mood_valence = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Emotional valence: -1 (negative) to 1 (positive)"
    )
    mood_arousal = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Emotional arousal: -1 (low energy) to 1 (high energy)"
    )
    
    # Custom manager
    objects = VizzyChatMessageManager()
    
    class Meta:
        db_table = 'vizzy_chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at'], name='vizzy_msg_sess_created_idx'),
            models.Index(fields=['role', 'created_at'], name='vizzy_msg_role_created_idx'),
            models.Index(fields=['has_images'], name='vizzy_msg_has_images_idx'),
            models.Index(fields=['-created_at'], name='vizzy_msg_created_idx'),
        ]
        verbose_name = 'Vizzy Chat Message'
        verbose_name_plural = 'Vizzy Chat Messages'
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.role}: {preview}"
    
    def clean(self):
        """Validate message data"""
        if self.mood_valence is not None and not -1.0 <= self.mood_valence <= 1.0:
            raise ValidationError("Mood valence must be between -1.0 and 1.0")
        if self.mood_arousal is not None and not -1.0 <= self.mood_arousal <= 1.0:
            raise ValidationError("Mood arousal must be between -1.0 and 1.0")
        if self.has_images and not self.image_urls:
            raise ValidationError("has_images is True but no image_urls provided")
    
    def save(self, *args, **kwargs):
        """Override save to update session timestamps"""
        self.full_clean()
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # Update session metadata
        if is_new:
            self.session.last_message_at = self.created_at
            self.session.message_count = models.F('message_count') + 1
            self.session.save(update_fields=['last_message_at', 'message_count', 'updated_at'])


class VizzyUserProfile(models.Model):
    """
    Extended user profile for Vizzy personalization
    
    Stores user preferences, behavioral patterns, and context
    for enhanced AI personalization.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vizzy_profile',
        primary_key=True,
        help_text="Associated user account"
    )
    
    # Aesthetic preferences
    aesthetic_palette = models.JSONField(
        default=dict,
        blank=True,
        help_text="User's aesthetic preferences (colors, styles, themes)"
    )
    
    # Behavioral patterns
    mood_map = models.JSONField(
        default=dict,
        blank=True,
        help_text="Historical mood patterns and trends"
    )
    story_markers = models.JSONField(
        default=list,
        blank=True,
        help_text="Important memories, milestones, and life events"
    )
    
    # Device context
    device_context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Device configuration (room types, display schedule, etc.)"
    )
    
    # Engagement metrics
    total_sessions = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total number of chat sessions"
    )
    total_messages = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total number of messages sent"
    )
    last_active = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last activity timestamp"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Profile creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last profile update timestamp"
    )
    
    class Meta:
        db_table = 'vizzy_user_profiles'
        verbose_name = 'Vizzy User Profile'
        verbose_name_plural = 'Vizzy User Profiles'
    
    def __str__(self):
        return f"Vizzy Profile - {self.user.email}"
    
    def update_engagement(self, session_created=False, message_sent=False):
        """Update engagement metrics"""
        if session_created:
            self.total_sessions = models.F('total_sessions') + 1
        if message_sent:
            self.total_messages = models.F('total_messages') + 1
        self.last_active = timezone.now()
        self.save(update_fields=['total_sessions', 'total_messages', 'last_active', 'updated_at'])


class VizzyMoodHistoryManager(models.Manager):
    """Custom manager for VizzyMoodHistory"""
    
    def user_mood_timeline(self, user, days=30):
        """Get mood history for user over specified days"""
        since = timezone.now() - timezone.timedelta(days=days)
        return self.filter(user=user, timestamp__gte=since).order_by('timestamp')
    
    def recent_user_mood(self, user, limit=10):
        """Get most recent mood entries for user"""
        return self.filter(user=user).order_by('-timestamp')[:limit]
    
    def average_valence(self, user, days=7):
        """Calculate average valence for user over specified days"""
        from django.db.models import Avg
        since = timezone.now() - timezone.timedelta(days=days)
        result = self.filter(
            user=user,
            timestamp__gte=since
        ).aggregate(avg_valence=Avg('valence'))
        return result['avg_valence']


class VizzyMoodHistory(models.Model):
    """
    Track mood over time for emotional intelligence
    
    Stores emotional state data points for pattern recognition
    and personalized responses.
    """
    
    SOURCE_CHOICES = [
        ('text_analysis', 'Text Analysis'),
        ('explicit_input', 'Explicit User Input'),
        ('image_analysis', 'Image Analysis'),
        ('context_inference', 'Context Inference'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique mood entry identifier"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vizzy_moods',
        help_text="User whose mood is tracked"
    )
    session = models.ForeignKey(
        VizzyChatSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='mood_entries',
        help_text="Associated session (if any)"
    )
    
    # Emotion classification (valence-arousal model)
    valence = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Emotional valence: -1 (negative) to 1 (positive)"
    )
    arousal = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Emotional arousal: -1 (low energy) to 1 (high energy)"
    )
    emotion_label = models.CharField(
        max_length=50,
        help_text="Emotion label (joy, calm, stress, anger, etc.)"
    )
    
    # Context
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When mood was recorded"
    )
    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        help_text="How mood was determined"
    )
    
    # Optional metadata
    confidence = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence score for mood detection (0.0 to 1.0)"
    )
    
    # Custom manager
    objects = VizzyMoodHistoryManager()
    
    class Meta:
        db_table = 'vizzy_mood_history'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp'], name='vizzy_mood_user_time_idx'),
            models.Index(fields=['session', '-timestamp'], name='vizzy_mood_sess_time_idx'),
            models.Index(fields=['emotion_label'], name='vizzy_mood_label_idx'),
            models.Index(fields=['-timestamp'], name='vizzy_mood_time_idx'),
        ]
        verbose_name = 'Vizzy Mood History'
        verbose_name_plural = 'Vizzy Mood Histories'
    
    def __str__(self):
        return f"{self.user.email} - {self.emotion_label} ({self.timestamp})"
    
    def clean(self):
        """Validate mood data"""
        if not -1.0 <= self.valence <= 1.0:
            raise ValidationError("Valence must be between -1.0 and 1.0")
        if not -1.0 <= self.arousal <= 1.0:
            raise ValidationError("Arousal must be between -1.0 and 1.0")


class VizzyContextDataManager(models.Manager):
    """Custom manager for VizzyContextData"""
    
    def user_context(self, user, context_type=None):
        """Get context data for user, optionally filtered by type"""
        qs = self.filter(user=user)
        if context_type:
            qs = qs.filter(context_type=context_type)
        return qs.order_by('-accessed_at')
    
    def get_or_create_context(self, user, context_type, key, default_value):
        """Get or create context entry"""
        return self.get_or_create(
            user=user,
            context_type=context_type,
            key=key,
            defaults={'value': default_value}
        )
    
    def increment_access(self, context_id):
        """Increment access count for context entry"""
        self.filter(id=context_id).update(
            access_count=models.F('access_count') + 1,
            accessed_at=timezone.now()
        )


class VizzyContextData(models.Model):
    """
    Cacheable context data for RAG and personalization
    
    Stores various types of contextual information used to enhance
    AI responses with user-specific knowledge.
    """
    
    CONTEXT_TYPE_CHOICES = [
        ('preference', 'User Preference'),
        ('creation', 'Past Creation'),
        ('interaction', 'Interaction Pattern'),
        ('knowledge', 'Domain Knowledge'),
        ('metadata', 'Metadata'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique context entry identifier"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vizzy_context',
        help_text="Context owner"
    )
    
    # Context type
    context_type = models.CharField(
        max_length=50,
        choices=CONTEXT_TYPE_CHOICES,
        db_index=True,
        help_text="Type of context data"
    )
    
    # Data
    key = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Context key (e.g., 'favorite_color', 'preferred_style')"
    )
    value = models.JSONField(
        help_text="Context value (flexible JSON structure)"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When context was created"
    )
    accessed_at = models.DateTimeField(
        auto_now=True,
        help_text="Last access timestamp"
    )
    access_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of times accessed"
    )
    
    # Custom manager
    objects = VizzyContextDataManager()
    
    class Meta:
        db_table = 'vizzy_context_data'
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['user', 'context_type'], name='vizzy_ctx_user_type_idx'),
            models.Index(fields=['key'], name='vizzy_ctx_key_idx'),
            models.Index(fields=['user', 'key'], name='vizzy_ctx_user_key_idx'),
            models.Index(fields=['-accessed_at'], name='vizzy_ctx_accessed_idx'),
        ]
        unique_together = [['user', 'context_type', 'key']]
        verbose_name = 'Vizzy Context Data'
        verbose_name_plural = 'Vizzy Context Data'
    
    def __str__(self):
        return f"{self.user.email} - {self.context_type}: {self.key}"
    
    def increment_access(self):
        """Increment access count"""
        self.access_count = models.F('access_count') + 1
        self.accessed_at = timezone.now()
        self.save(update_fields=['access_count', 'accessed_at'])
