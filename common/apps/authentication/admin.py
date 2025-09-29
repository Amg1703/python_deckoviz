from django.contrib import admin
from .models import DeviceLink

@admin.register(DeviceLink)
class DeviceLinkAdmin(admin.ModelAdmin):
	list_display = ("user", "device_type", "created_at", "expires_at")
	search_fields = ("user__username", "device_type")
	
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User,NewsLetterSubscriber

admin.site.unregister(Group)

# Register your models here.
admin.site.register(User)
admin.site.register(NewsLetterSubscriber)