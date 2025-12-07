from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MusicTaskInternalViewSet, LyricsInternalViewSet, MusicVideoInternalViewSet

router = DefaultRouter()
router.register(r'tasks', MusicTaskInternalViewSet, basename='music-task-internal')
router.register(r'lyrics', LyricsInternalViewSet, basename='lyrics-internal')
router.register(r'videos', MusicVideoInternalViewSet, basename='music-video-internal')

urlpatterns = [
    path('', include(router.urls)),
]
