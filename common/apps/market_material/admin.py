from django.contrib import admin
from .models import MarketingMaterial, BrandAsset


@admin.register(MarketingMaterial)
class MarketingMaterialAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'request_id',
        'user_id',
        'material_type',
        'tone',
        'status',
        'num_outputs',
        'created_at',
    ]
    list_filter = ['status', 'material_type', 'tone', 'created_at']
    search_fields = ['request_id', 'user_id', 'prompt', 'campaign_goal']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'user_id', 'status')
        }),
        ('Content', {
            'fields': ('prompt', 'campaign_goal', 'tone', 'material_type')
        }),
        ('Configuration', {
            'fields': ('aspect_ratio', 'num_outputs')
        }),
        ('Results', {
            'fields': ('materials', 'text_suggestions', 'error'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(BrandAsset)
class BrandAssetAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'asset_id',
        'user_id',
        'filename',
        'file_type',
        'uploaded_at',
    ]
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['asset_id', 'user_id', 'filename']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Asset Information', {
            'fields': ('asset_id', 'user_id', 'filename', 'file_type')
        }),
        ('File Details', {
            'fields': ('file_path',)
        }),
        ('Extracted Data', {
            'fields': ('extracted_colors', 'extracted_text'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',)
        }),
    )
