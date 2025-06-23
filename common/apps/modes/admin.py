from django.contrib import admin
from .models import Mode, Music, UserMode, Session

@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('admin_collections', 'admin_music')

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('name', 'file')

@admin.register(UserMode)
class UserModeAdmin(admin.ModelAdmin):
    list_display = ('user', 'mode')
    filter_horizontal = ('user_collections', 'user_music')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'mode', 'purpose', 'duration', 'is_active')
    list_filter = ('mode', 'purpose', 'is_active')
    search_fields = ('user__username', 'intention')
