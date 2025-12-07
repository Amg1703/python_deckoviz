from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MarketingMaterialInternalViewSet, BrandAssetInternalViewSet

router = DefaultRouter()
router.register(r'materials', MarketingMaterialInternalViewSet, basename='material')
router.register(r'assets', BrandAssetInternalViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]
