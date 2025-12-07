from django.contrib import admin
from .models import PDF, Job, Image


@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'pages_count', 'size_mb', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'extracted_text')
    readonly_fields = ('id', 'uploaded_at', 'size_mb')
    ordering = ('-uploaded_at',)
    
    def size_mb(self, obj):
        return f"{obj.size_bytes / (1024 * 1024):.2f} MB"
    size_mb.short_description = 'Size'
    
    fieldsets = (
        ('File Information', {
            'fields': ('id', 'filename', 'size_bytes', 'size_mb', 'pages_count', 'uploaded_at')
        }),
        ('Content', {
            'fields': ('extracted_text',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf', 'status', 'page_number', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'prompt', 'pdf__filename')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'pdf')
        }),
        ('Request Details', {
            'fields': ('prompt', 'page_number', 'chapter_number')
        }),
        ('Status', {
            'fields': ('status', 'error')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'provider', 'dimensions', 'created_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('id', 'provider_job_id')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    def dimensions(self, obj):
        if obj.width and obj.height:
            return f"{obj.width} x {obj.height}"
        return "N/A"
    dimensions.short_description = 'Dimensions'
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'job')
        }),
        ('Provider Details', {
            'fields': ('provider', 'provider_job_id')
        }),
        ('Image Properties', {
            'fields': ('width', 'height', 'mime')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
