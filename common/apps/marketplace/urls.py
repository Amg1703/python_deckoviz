from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceViewSet

router = DefaultRouter()
# router.register('prices', PriceViewSet,basename='prices')
 
urlpatterns = [
    path('', include(router.urls)),
]
