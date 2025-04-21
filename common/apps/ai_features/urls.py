from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StyleOptionViewSet, StyledImageViewSet, AIGeneratedImageViewSet

router = DefaultRouter()
router.register(r'styles', StyleOptionViewSet, basename='styles')
router.register(r'styled-images', StyledImageViewSet, basename='styled-images')
router.register(r'generated-images', AIGeneratedImageViewSet, basename='generated-images')

urlpatterns = [
    path('', include(router.urls)),
]
