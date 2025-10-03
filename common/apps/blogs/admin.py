from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Blog,Asset
        
@admin.register(Asset)
class AssetAdmin(ModelAdmin):
    list_display = ('file', )
    search_fields = ('file',) 

@admin.register(Blog)
class BlogAdmin(ModelAdmin):
    list_display = ('title', 'created_at','delete_status', 'id', )
    search_fields = ('title', 'tags')
    ordering = ('-created_at',)
    list_filter = ('created_at',)

