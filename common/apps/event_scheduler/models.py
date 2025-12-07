from django.db import models
from django.contrib.auth import get_user_model
from apps.authentication.models import BaseModel

User = get_user_model()


class EventType(models.TextChoices):
    SUNRISE = "sunrise", "Sunrise"
    SUNSET = "sunset", "Sunset"
    CUSTOM_TIME = "custom_time", "Custom Time"
    OCCASION = "occasion", "Occasion"
    AUDIENCE_TRIGGER = "audience", "Audience Trigger"


class ScheduleType(models.TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    HOURLY = "hourly", "Hourly"
    INTERVAL = "interval", "Interval"
    ONCE = "once", "Once"


class Event(BaseModel):
    """Scheduled events for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_events')
    event_name = models.CharField(max_length=255)
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        db_index=True
    )
    
    # Scheduling
    trigger_time = models.CharField(max_length=10)  # UTC time HH:MM
    trigger_time_local = models.CharField(max_length=10, null=True, blank=True)  # Local time HH:MM
    schedule_type = models.CharField(
        max_length=50,
        choices=ScheduleType.choices,
        db_index=True
    )
    timezone = models.CharField(max_length=50, default="UTC")
    
    # Weekly/Interval specific
    day_of_week = models.CharField(max_length=20, null=True, blank=True)
    interval_minutes = models.IntegerField(null=True, blank=True)
    
    # Execution limits
    max_executions = models.IntegerField(null=True, blank=True)
    execution_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Visual configuration
    visual_config = models.JSONField(default=dict)
    
    # Metadata
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    # Status
    enabled = models.BooleanField(default=True, db_index=True)
    
    # Execution tracking
    last_execution = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(null=True, blank=True)
    last_error_time = models.DateTimeField(null=True, blank=True)
    
    # Generated image
    generated_image = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'events'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['enabled', 'event_type']),
            models.Index(fields=['schedule_type']),
        ]
    
    def __str__(self):
        return f"{self.event_name} ({self.user.username}) - {self.event_type}"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user.id),
            "event_name": self.event_name,
            "event_type": self.event_type,
            "trigger_time": self.trigger_time,
            "trigger_time_local": self.trigger_time_local,
            "schedule_type": self.schedule_type,
            "timezone": self.timezone,
            "day_of_week": self.day_of_week,
            "interval_minutes": self.interval_minutes,
            "max_executions": self.max_executions,
            "execution_count": self.execution_count,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "visual_config": self.visual_config,
            "location": self.location,
            "description": self.description,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "last_error": self.last_error,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "generated_image": self.generated_image
        }
