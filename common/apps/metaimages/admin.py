from django.contrib import admin
from .models import MetaImage, SharedImage

admin.site.register(MetaImage)

@admin.register(SharedImage)
class SharedImageAdmin(admin.ModelAdmin):
    list_display = ['image', 'owner', 'shared_with', 'shared_at']
    list_filter = ['shared_at']
    search_fields = ['owner__username', 'owner__email', 'shared_with__username', 'shared_with__email']
    readonly_fields = ['shared_at'] 