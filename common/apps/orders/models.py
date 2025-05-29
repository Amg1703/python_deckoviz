from apps.authentication.models import BaseModel
from django.db import models
from django.contrib.auth import get_user_model
from apps.utils.choices import ORDER_STATUS_CHOICES,STATUS_DICT
from .managers import OrderManager, OrderDetailManager

User = get_user_model()


class Order(BaseModel): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    billing_address = models.JSONField()
    shipping_address = models.JSONField()
    status = models.CharField(max_length=255, choices=ORDER_STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"{self.user.username} - {self.id}"
    
    objects = OrderManager()
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        

class OrderDetail(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_details')
    image = models.ForeignKey('gallery.Image', on_delete=models.PROTECT, related_name='order_details')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True) 
    status = models.CharField(max_length=255, choices=ORDER_STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField(default=1)
    overall_status = models.PositiveIntegerField(default=1,null=True,blank=True,choices=STATUS_DICT.keys())
    
    def __str__(self):
        return f"{self.order.user.username} - {self.id}"
    
    objects = OrderDetailManager()
    
    class Meta:
        db_table = 'order_details'
        verbose_name = 'Order Detail'
        verbose_name_plural = 'Order Details'