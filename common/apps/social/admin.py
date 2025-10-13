from django.contrib import admin
from .models import SocialConnection, ImageInteraction, CollectionInteraction

@admin.register(SocialConnection)
class SocialConnectionAdmin(admin.ModelAdmin):
    list_display = ("user", "connection", "created_at")
    search_fields = ("user__email", "connection__email")
    list_filter = ("created_at",)

@admin.register(ImageInteraction)
class ImageInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "image", "interaction_type", "created_at")
    search_fields = ("user__email", "image__id")
    list_filter = ("interaction_type", "created_at")

@admin.register(CollectionInteraction)
class CollectionInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "collection", "interaction_type", "created_at")
    search_fields = ("user__email", "collection__id")
    list_filter = ("interaction_type", "created_at")
