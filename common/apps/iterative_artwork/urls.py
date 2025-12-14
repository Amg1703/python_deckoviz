from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IterativeArtworkInternalViewSet, IterativeArtworkIterationInternalViewSet

router = DefaultRouter()
router.register(r'artworks', IterativeArtworkInternalViewSet, basename='artwork')
router.register(r'iterations', IterativeArtworkIterationInternalViewSet, basename='iteration')

urlpatterns = [
    path('', include(router.urls)),
]
