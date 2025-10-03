from django.contrib.admin import ModelAdmin
from django.contrib import admin
from .models import Review 


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('customer', 'customer_rating', 'created_at', 'is_active')
    search_fields = ('customer__username', 'comment')
    list_filter = ('created_at', 'is_active')
    ordering = ('-created_at',)
