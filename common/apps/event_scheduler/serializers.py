from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, EventType, ScheduleType

User = get_user_model()


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event objects"""
    
    user_id = serializers.CharField(source='user.id', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'user', 'user_id', 'event_name', 'event_type',
            'trigger_time', 'trigger_time_local', 'schedule_type', 'timezone',
            'day_of_week', 'interval_minutes', 'max_executions', 'execution_count',
            'expires_at', 'visual_config', 'location', 'description',
            'enabled', 'last_execution', 'last_error', 'last_error_time',
            'generated_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at', 'execution_count', 
                           'last_execution', 'last_error', 'last_error_time']


class EventCreateRequestSerializer(serializers.Serializer):
    """Serializer for creating an event"""
    
    user_id = serializers.CharField(required=True)
    event_name = serializers.CharField(max_length=255, required=True)
    event_type = serializers.ChoiceField(choices=EventType.choices, required=True)
    trigger_time = serializers.CharField(max_length=10, required=True)
    trigger_time_local = serializers.CharField(max_length=10, required=False, allow_blank=True)
    schedule_type = serializers.ChoiceField(choices=ScheduleType.choices, required=True)
    timezone = serializers.CharField(max_length=50, default="UTC")
    day_of_week = serializers.CharField(max_length=20, required=False, allow_blank=True)
    interval_minutes = serializers.IntegerField(required=False, allow_null=True)
    max_executions = serializers.IntegerField(required=False, allow_null=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    visual_config = serializers.JSONField(required=True)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    enabled = serializers.BooleanField(default=True)


class EventUpdateSerializer(serializers.Serializer):
    """Serializer for updating event fields"""
    
    event_name = serializers.CharField(max_length=255, required=False)
    trigger_time = serializers.CharField(max_length=10, required=False)
    trigger_time_local = serializers.CharField(max_length=10, required=False, allow_blank=True)
    schedule_type = serializers.ChoiceField(choices=ScheduleType.choices, required=False)
    timezone = serializers.CharField(max_length=50, required=False)
    day_of_week = serializers.CharField(max_length=20, required=False, allow_blank=True)
    interval_minutes = serializers.IntegerField(required=False, allow_null=True)
    visual_config = serializers.JSONField(required=False)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    enabled = serializers.BooleanField(required=False)
    generated_image = serializers.CharField(max_length=255, required=False, allow_blank=True)


class EventExecutionUpdateSerializer(serializers.Serializer):
    """Serializer for updating event execution stats"""
    
    error = serializers.CharField(required=False, allow_blank=True, allow_null=True)
