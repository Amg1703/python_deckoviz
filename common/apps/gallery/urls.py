from django.urls import path,include,re_path 
from rest_framework.routers import DefaultRouter 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (ImageViewSet,CollectionViewSet,CollectionImageViewSet)

router = DefaultRouter()

router.register(r'images', ImageViewSet,basename='images')
router.register(r'collections', CollectionViewSet,basename='collections')
router.register(r'collection-images', CollectionImageViewSet,basename='collection_images')


urlpatterns = [
    path('',include(router.urls)),
]
