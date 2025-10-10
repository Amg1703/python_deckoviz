from django.db import models
from apps.authentication.models import BaseModel
from .managers import PriceManager
from apps.utils.choices import SIZE_CHOICES,CANVAS_RATIO



class Price(BaseModel):
    image = models.OneToOneField('gallery.Image', on_delete=models.CASCADE, related_name='prices', unique=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=255, default='S', choices=SIZE_CHOICES)
    canvas_ratio = models.CharField(max_length=255, default='16:9', blank=True, null=True, choices=CANVAS_RATIO)
    is_active = models.BooleanField(default=True)

    objects = PriceManager()

    def __str__(self):
        return f"Price {self.id}"

    class Meta:
        db_table = 'prices'
        verbose_name = 'Price'
        verbose_name_plural = 'Prices'
        indexes = [
            models.Index(fields=['final_price']),
        ]

# --- Product Model ---
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.ForeignKey(Price, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# --- Cart and CartItem ---
from django.conf import settings

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price.final_price * self.quantity

# --- Coupon ---
from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(default=10)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

    def apply_discount(self, amount):
        if self.is_valid():
            return (self.discount_percent / 100) * amount
        return 0

# --- Order and OrderItem ---
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)

    def calculate_total(self):
        total = sum(item.get_total_price() for item in self.items.all())
        if self.coupon:
            total -= self.coupon.apply_discount(total)
        self.total_price = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price.final_price * self.quantity
        

    
    