from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CollectionNarrationInternalViewSet

router = DefaultRouter()
router.register(r'narrations', CollectionNarrationInternalViewSet, basename='narration')

urlpatterns = [
    path('', include(router.urls)),
]
