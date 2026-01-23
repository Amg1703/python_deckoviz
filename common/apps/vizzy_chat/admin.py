"""
Vizzy Chat Django Admin Configuration

Production-ready admin interface with:
- Efficient queries (select_related, prefetch_related)
- Searchable fields
- Filters
- Read-only fields
- Custom actions
- Inline editing where appropriate
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import (
    VizzyChatSession,
    VizzyChatMessage,
    VizzyUserProfile,
    VizzyMoodHistory,
    VizzyContextData
)


class VizzyChatMessageInline(admin.TabularInline):
    """Inline display of messages within session admin"""
    model = VizzyChatMessage
    extra = 0
    fields = ['role', 'content_preview', 'created_at', 'detected_emotion', 'tokens_used']
    readonly_fields = ['content_preview', 'created_at']
    can_delete = False
    show_change_link = True
    
    def content_preview(self, obj):
        """Show truncated content"""
        if obj.content:
            preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
            return format_html('<span style="font-family: monospace;">{}</span>', preview)
        return '-'
    content_preview.short_description = 'Content Preview'
    
    def has_add_permission(self, request, obj=None):
        """Disable adding messages through admin"""
        return False


@admin.register(VizzyChatSession)
class VizzyChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for chat sessions"""
    
    list_display = [
        'id',
        'user_email',
        'title',
        'mode',
        'is_active',
        'message_count',
        'last_message_at',
        'created_at',
    ]
    list_filter = [
        'mode',
        'is_active',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'id',
        'user__email',
        'user__first_name',
        'user__last_name',
        'title',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'closed_at',
        'message_count',
        'last_message_at',
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'mode')
        }),
        ('Status', {
            'fields': ('is_active', 'message_count', 'last_message_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [VizzyChatMessageInline]
    date_hierarchy = 'created_at'
    
    # Performance optimization
    list_select_related = ['user']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('user').annotate(
            actual_message_count=Count('messages')
        )
    
    actions = ['close_sessions', 'activate_sessions']
    
    def close_sessions(self, request, queryset):
        """Bulk close sessions"""
        from django.utils import timezone
        updated = queryset.filter(is_active=True).update(
            is_active=False,
            closed_at=timezone.now()
        )
        self.message_user(request, f'{updated} sessions closed successfully.')
    close_sessions.short_description = 'Close selected sessions'
    
    def activate_sessions(self, request, queryset):
        """Bulk activate sessions"""
        updated = queryset.filter(is_active=False).update(
            is_active=True,
            closed_at=None
        )
        self.message_user(request, f'{updated} sessions activated successfully.')
    activate_sessions.short_description = 'Activate selected sessions'


@admin.register(VizzyChatMessage)
class VizzyChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for chat messages"""
    
    list_display = [
        'id',
        'session_id',
        'user_email',
        'role',
        'content_preview',
        'has_images',
        'detected_emotion',
        'created_at',
    ]
    list_filter = [
        'role',
        'has_images',
        'detected_emotion',
        'created_at',
    ]
    search_fields = [
        'id',
        'session__id',
        'session__user__email',
        'content',
    ]
    readonly_fields = [
        'id',
        'session',
        'role',
        'content',
        'has_images',
        'image_urls',
        'created_at',
        'tokens_used',
        'processing_time_ms',
        'detected_emotion',
        'mood_valence',
        'mood_arousal',
    ]
    fieldsets = (
        ('Message Information', {
            'fields': ('id', 'session', 'role', 'content')
        }),
        ('Multimodal Content', {
            'fields': ('has_images', 'image_urls'),
            'classes': ('collapse',)
        }),
        ('Emotional Context', {
            'fields': ('detected_emotion', 'mood_valence', 'mood_arousal'),
            'classes': ('collapse',)
        }),
        ('Performance Metrics', {
            'fields': ('tokens_used', 'processing_time_ms', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'
    
    # Performance optimization
    list_select_related = ['session', 'session__user']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.session.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'session__user__email'
    
    def content_preview(self, obj):
        """Show truncated content"""
        if obj.content:
            preview = obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
            return format_html('<span style="font-family: monospace; font-size: 11px;">{}</span>', preview)
        return '-'
    content_preview.short_description = 'Content'
    
    def session_id(self, obj):
        """Display session ID with link"""
        return format_html(
            '<a href="/admin/vizzy_chat/vizzychatsession/{}/change/">{}</a>',
            obj.session.id,
            str(obj.session.id)[:8] + '...'
        )
    session_id.short_description = 'Session'
    
    def has_add_permission(self, request):
        """Disable adding messages through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make messages read-only"""
        return False


@admin.register(VizzyUserProfile)
class VizzyUserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles"""
    
    list_display = [
        'user_email',
        'total_sessions',
        'total_messages',
        'last_active',
        'created_at',
    ]
    list_filter = [
        'last_active',
        'created_at',
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
    ]
    readonly_fields = [
        'user',
        'total_sessions',
        'total_messages',
        'last_active',
        'created_at',
        'updated_at',
    ]
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('aesthetic_palette', 'device_context')
        }),
        ('Behavioral Data', {
            'fields': ('mood_map', 'story_markers'),
            'classes': ('collapse',)
        }),
        ('Engagement Metrics', {
            'fields': ('total_sessions', 'total_messages', 'last_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'last_active'
    
    # Performance optimization
    list_select_related = ['user']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of profiles"""
        return False


class VizzyMoodHistoryFilter(admin.SimpleListFilter):
    """Custom filter for mood valence ranges"""
    title = 'mood valence'
    parameter_name = 'valence_range'
    
    def lookups(self, request, model_admin):
        return [
            ('positive', 'Positive (> 0.3)'),
            ('neutral', 'Neutral (-0.3 to 0.3)'),
            ('negative', 'Negative (< -0.3)'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'positive':
            return queryset.filter(valence__gt=0.3)
        if self.value() == 'neutral':
            return queryset.filter(valence__gte=-0.3, valence__lte=0.3)
        if self.value() == 'negative':
            return queryset.filter(valence__lt=-0.3)
        return queryset


@admin.register(VizzyMoodHistory)
class VizzyMoodHistoryAdmin(admin.ModelAdmin):
    """Admin interface for mood history"""
    
    list_display = [
        'timestamp',
        'user_email',
        'emotion_label',
        'valence_display',
        'arousal_display',
        'source',
        'confidence_display',
    ]
    list_filter = [
        VizzyMoodHistoryFilter,
        'emotion_label',
        'source',
        'timestamp',
    ]
    search_fields = [
        'user__email',
        'session__id',
        'emotion_label',
    ]
    readonly_fields = [
        'id',
        'user',
        'session',
        'valence',
        'arousal',
        'emotion_label',
        'timestamp',
        'source',
        'confidence',
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'session', 'timestamp')
        }),
        ('Emotional Data', {
            'fields': ('emotion_label', 'valence', 'arousal', 'confidence')
        }),
        ('Metadata', {
            'fields': ('source',),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'timestamp'
    
    # Performance optimization
    list_select_related = ['user', 'session']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def valence_display(self, obj):
        """Display valence with color coding"""
        if obj.valence > 0.3:
            color = 'green'
        elif obj.valence < -0.3:
            color = 'red'
        else:
            color = 'orange'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color,
            obj.valence
        )
    valence_display.short_description = 'Valence'
    valence_display.admin_order_field = 'valence'
    
    def arousal_display(self, obj):
        """Display arousal with color coding"""
        if obj.arousal > 0.3:
            color = 'darkblue'
        elif obj.arousal < -0.3:
            color = 'gray'
        else:
            color = 'black'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color,
            obj.arousal
        )
    arousal_display.short_description = 'Arousal'
    arousal_display.admin_order_field = 'arousal'
    
    def confidence_display(self, obj):
        """Display confidence percentage"""
        if obj.confidence is not None:
            return f'{obj.confidence * 100:.1f}%'
        return '-'
    confidence_display.short_description = 'Confidence'
    confidence_display.admin_order_field = 'confidence'
    
    def has_add_permission(self, request):
        """Disable adding mood entries through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make mood history read-only"""
        return False


@admin.register(VizzyContextData)
class VizzyContextDataAdmin(admin.ModelAdmin):
    """Admin interface for context data"""
    
    list_display = [
        'user_email',
        'context_type',
        'key',
        'access_count',
        'accessed_at',
        'created_at',
    ]
    list_filter = [
        'context_type',
        'created_at',
        'accessed_at',
    ]
    search_fields = [
        'user__email',
        'key',
        'value',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'accessed_at',
        'access_count',
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'context_type', 'key')
        }),
        ('Data', {
            'fields': ('value',)
        }),
        ('Metadata', {
            'fields': ('access_count', 'created_at', 'accessed_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'accessed_at'
    
    # Performance optimization
    list_select_related = ['user']
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    actions = ['reset_access_count']
    
    def reset_access_count(self, request, queryset):
        """Reset access count for selected entries"""
        updated = queryset.update(access_count=0)
        self.message_user(request, f'Access count reset for {updated} entries.')
    reset_access_count.short_description = 'Reset access count'
