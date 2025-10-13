
from django.contrib import admin
from .models import Price, Product, Cart, CartItem, Order, OrderItem, Coupon

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
	list_display = ("id", "image", "final_price", "size", "canvas_ratio", "is_active", "created_at", "updated_at")
	list_filter = ("is_active", "size", "canvas_ratio")
	search_fields = ("id",)
	ordering = ("-created_at",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "active", "price", "created_at", "updated_at")
	list_filter = ("active",)
	search_fields = ("name",)
	ordering = ("-created_at",)

class CartItemInline(admin.TabularInline):
	model = CartItem
	extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "created_at", "updated_at")
	search_fields = ("user__email", "id")
	inlines = [CartItemInline]
	ordering = ("-created_at",)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ("id", "cart", "product", "quantity")
	search_fields = ("cart__id", "product__name")

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
	list_display = ("id", "code", "discount_percent", "active", "valid_from", "valid_to")
	list_filter = ("active",)
	search_fields = ("code",)
	ordering = ("-valid_from",)

class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "status", "total_price", "coupon", "created_at")
	list_filter = ("status",)
	search_fields = ("user__email", "id")
	inlines = [OrderItemInline]
	ordering = ("-created_at",)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ("id", "order", "product", "quantity")
	search_fields = ("order__id", "product__name")
