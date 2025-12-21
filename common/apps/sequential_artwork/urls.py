from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SequentialArtworkViewSet, SequentialArtworkIterationViewSet

router = DefaultRouter()
router.register(r'artworks', SequentialArtworkViewSet, basename='sequential-artwork')
router.register(r'iterations', SequentialArtworkIterationViewSet, basename='artwork-iteration')

urlpatterns = [
    path('', include(router.urls)),
]