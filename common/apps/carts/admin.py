from .models import Cart
from django.contrib import admin

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image', 'price', 'shipping_cost', 'quantity')
    list_filter = ('user', 'image', 'price', 'shipping_cost', 'quantity')
    search_fields = ('user', 'image', 'price', 'shipping_cost', 'quantity')
    ordering = ('-id',)
