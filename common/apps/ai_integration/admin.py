from django.contrib import admin
from .models import AIModel, AIOperation, AICallback

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'provider', 'version', 'is_active')
    list_filter = ('model_type', 'provider', 'is_active')
    search_fields = ('name', 'description', 'model_id')
    fieldsets = (
        (None, {
            'fields': ('name', 'model_type', 'provider', 'model_id', 'version', 'description')
        }),
        ('Configuration', {
            'fields': ('is_active', 'config')
        }),
    )

@admin.register(AIOperation)
class AIOperationAdmin(admin.ModelAdmin):
    list_display = ('user', 'operation_type', 'model', 'status', 'credits_used', 'created_at')
    list_filter = ('operation_type', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'error_message')
    readonly_fields = ('created_at', 'updated_at', 'processing_time')
    fieldsets = (
        (None, {
            'fields': ('user', 'operation_type', 'model', 'status')
        }),
        ('Data', {
            'fields': ('input_data', 'result_data', 'error_message')
        }),
        ('Metrics', {
            'fields': ('credits_used', 'processing_time', 'external_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(AICallback)
class AICallbackAdmin(admin.ModelAdmin):
    list_display = ('operation', 'processed', 'created_at')
    list_filter = ('processed', 'created_at')
    search_fields = ('operation__id', 'operation__user__username')
    readonly_fields = ('created_at', 'updated_at')
