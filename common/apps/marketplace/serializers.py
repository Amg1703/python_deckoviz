from rest_framework import serializers
# --- ProductSerializer ---
from .models import Price, Product, Cart, CartItem, Order, OrderItem, Coupon
class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = [
            'id',
            'image',
            'final_price',
            'created_at',
            'updated_at'
        ]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# --- Cart & CartItem Serializers ---
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = '__all__'

# --- Order & OrderItem Serializers ---
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = '__all__'

# --- CouponSerializer ---
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


