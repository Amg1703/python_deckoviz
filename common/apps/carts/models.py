from django.db import models
from apps.authentication.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.OneToOneField('gallery.Image', on_delete=models.PROTECT, related_name='carts', null=False, blank=False)
    price = models.OneToOneField('marketplace.Price', on_delete=models.PROTECT, related_name='carts', null=False, blank=False)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Cart for {self.user.username}"
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        indexes = [
            models.Index(fields=['user']),
        ]