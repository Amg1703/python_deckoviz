from apps.authentication.models import BaseModel
from django.db import models
from django.contrib.auth import get_user_model
from apps.utils.choices import ORDER_STATUS_CHOICES
from .managers import OrderManager

User = get_user_model()


class Order(BaseModel): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    price = models.ForeignKey('marketplace.Price', on_delete=models.CASCADE, related_name='orders')
    billing_address = models.JSONField()
    shipping_address = models.JSONField()
    status = models.CharField(max_length=255, choices=ORDER_STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.id}"
    
    objects = OrderManager()
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        
    