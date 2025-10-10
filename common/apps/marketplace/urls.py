from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceViewSet, ProductViewSet, CartViewSet, OrderViewSet, CouponViewSet

router = DefaultRouter()
router.register(r'prices', PriceViewSet, basename='price')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
]
