from django.contrib import admin
from .models import FeatureUsage, UserSession, DailyUserStats, FeaturePricing
import json


@admin.register(FeatureUsage)
class FeatureUsageAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'feature_name', 'feature_category', 'status', 
        'credits_used', 'processing_time', 'created_at'
    )
    list_filter = (
        'feature_name', 'feature_category', 'status', 'created_at'
    )
    search_fields = ('user__username', 'user__email', 'feature_name', 'session_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'feature_name', 'feature_category', 'session_id', 'status')
        }),
        ('Usage Details', {
            'fields': ('credits_used', 'processing_time', 'endpoint_path')
        }),
        ('Request Context', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Data', {
            'fields': ('input_data_display', 'output_data_display'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message', 'error_code'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def input_data_display(self, obj):
        if obj.input_data:
            return json.dumps(obj.input_data, indent=2)
        return "No input data"
    input_data_display.short_description = "Input Data (JSON)"
    
    def output_data_display(self, obj):
        if obj.output_data:
            return json.dumps(obj.output_data, indent=2)
        return "No output data"
    output_data_display.short_description = "Output Data (JSON)"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'credit_operation')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'session_id', 'platform', 'is_active', 
        'total_ai_features_used', 'total_credits_spent', 'start_time'
    )
    list_filter = ('platform', 'is_active', 'start_time')
    search_fields = ('user__username', 'user__email', 'session_id', 'ip_address')
    readonly_fields = ('id', 'session_id', 'start_time', 'last_activity', 'end_time')
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'session_id', 'platform', 'is_active')
        }),
        ('Timing', {
            'fields': ('start_time', 'last_activity', 'end_time')
        }),
        ('Usage Statistics', {
            'fields': ('total_ai_features_used', 'total_credits_spent', 'total_requests')
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent', 'device_info_display'),
            'classes': ('collapse',)
        })
    )
    
    def device_info_display(self, obj):
        if obj.device_info:
            return json.dumps(obj.device_info, indent=2)
        return "No device info"
    device_info_display.short_description = "Device Info (JSON)"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(DailyUserStats)
class DailyUserStatsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'date', 'total_ai_requests', 'unique_features_used',
        'total_credits_spent', 'success_rate_display'
    )
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date')
        }),
        ('Usage Statistics', {
            'fields': (
                'total_ai_requests', 'unique_features_used', 'total_credits_spent',
                'successful_requests', 'failed_requests'
            )
        }),
        ('Breakdowns', {
            'fields': ('feature_breakdown_display', 'category_breakdown_display'),
            'classes': ('collapse',)
        }),
        ('Session Info', {
            'fields': ('total_session_time',),
            'classes': ('collapse',)
        })
    )
    
    def success_rate_display(self, obj):
        if obj.total_ai_requests == 0:
            return "0%"
        rate = (obj.successful_requests / obj.total_ai_requests) * 100
        return f"{rate:.1f}%"
    success_rate_display.short_description = "Success Rate"
    
    def feature_breakdown_display(self, obj):
        if obj.feature_usage_breakdown:
            return json.dumps(obj.feature_usage_breakdown, indent=2)
        return "No feature breakdown"
    feature_breakdown_display.short_description = "Feature Usage Breakdown (JSON)"
    
    def category_breakdown_display(self, obj):
        if obj.category_usage_breakdown:
            return json.dumps(obj.category_usage_breakdown, indent=2)
        return "No category breakdown"
    category_breakdown_display.short_description = "Category Usage Breakdown (JSON)"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(FeaturePricing)
class FeaturePricingAdmin(admin.ModelAdmin):
    list_display = (
        'feature_name', 'base_credits', 'per_unit_credits', 
        'tier_1_limit', 'is_active', 'updated_at'
    )
    list_filter = ('is_active', 'feature_name')
    search_fields = ('feature_name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Pricing', {
            'fields': ('feature_name', 'base_credits', 'per_unit_credits', 'description')
        }),
        ('Tier Pricing', {
            'fields': ('tier_1_limit', 'tier_1_price', 'tier_2_price', 'tier_3_price'),
            'description': 'Configure different pricing tiers for users'
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
    
    actions = ['enable_pricing', 'disable_pricing']
    
    def enable_pricing(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Enabled {queryset.count()} pricing configurations.")
    enable_pricing.short_description = "Enable selected pricing configurations"
    
    def disable_pricing(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Disabled {queryset.count()} pricing configurations.")
    disable_pricing.short_description = "Disable selected pricing configurations"


# Custom admin actions
def export_usage_data(modeladmin, request, queryset):
    """Export usage data to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="feature_usage_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'User', 'Feature Name', 'Category', 'Status', 'Credits Used',
        'Processing Time', 'Created At', 'Error Message'
    ])
    
    for usage in queryset:
        writer.writerow([
            usage.user.username,
            usage.feature_name,
            usage.feature_category,
            usage.status,
            usage.credits_used,
            usage.processing_time or '',
            usage.created_at.isoformat(),
            usage.error_message or ''
        ])
    
    return response

export_usage_data.short_description = "Export selected usage records to CSV"

# Add the action to FeatureUsageAdmin
FeatureUsageAdmin.actions = [export_usage_data]
