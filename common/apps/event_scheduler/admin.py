from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'event_name', 'user', 'event_type', 'schedule_type', 'trigger_time', 'enabled', 'execution_count', 'created_at']
    list_filter = ['event_type', 'schedule_type', 'enabled', 'created_at']
    search_fields = ['event_name', 'user__username', 'user__email', 'description', 'location']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at', 'execution_count', 'last_execution', 'last_error_time']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'event_name', 'event_type', 'description', 'enabled')
        }),
        ('Scheduling', {
            'fields': ('trigger_time', 'trigger_time_local', 'schedule_type', 'timezone', 
                      'day_of_week', 'interval_minutes')
        }),
        ('Execution Limits', {
            'fields': ('max_executions', 'execution_count', 'expires_at')
        }),
        ('Visual Configuration', {
            'fields': ('visual_config', 'generated_image')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Execution Tracking', {
            'fields': ('last_execution', 'last_error', 'last_error_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
