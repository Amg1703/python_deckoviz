from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderView,OrderDetailView

router = DefaultRouter()

router.register('orders', OrderView,basename='orders')
router.register('order-details', OrderDetailView,basename='order-details')
 
urlpatterns = [
    path('', include(router.urls)),
]
