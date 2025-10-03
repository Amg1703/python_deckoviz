from django.contrib import admin
from .models import Mode, Music, UserMode, Session

@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('admin_collections', 'admin_curations', 'admin_music')
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Collections & Curations', {
            'fields': ('admin_collections', 'admin_curations'),
            'description': 'Add collections to this mode. Collections can be either regular collections or curations (AI/admin recommended).'
        }),
        ('Music', {
            'fields': ('admin_music',),
        }),
    )

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('name', 'file')
    search_fields = ('name',)

@admin.register(UserMode)
class UserModeAdmin(admin.ModelAdmin):
    list_display = ('user', 'mode')
    list_filter = ('mode', 'user')
    filter_horizontal = ('user_collections', 'user_music')
    raw_id_fields = ('user', 'mode')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'mode', 'purpose', 'duration', 'is_active')
    list_filter = ('mode', 'purpose', 'is_active')
    search_fields = ('user__username', 'intention')
    raw_id_fields = ('user', 'mode')
