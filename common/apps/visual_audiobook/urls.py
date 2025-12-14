from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'audiobooks', views.VisualAudiobookViewSet, basename='audiobook')

urlpatterns = [
    # INTERNAL (unauthenticated) endpoints — MUST come before router include
    path('audiobooks/internal/create/', views.create_audiobook, name='visual_audiobook_create_internal'),  # POST from FastAPI
    path('audiobooks/internal/<str:audiobook_id>/', views.get_audiobook, name='visual_audiobook_get_internal'),  # GET
    path('audiobooks/internal/<str:audiobook_id>/update/', views.update_audiobook, name='visual_audiobook_update_internal'),  # PATCH
    path('audiobooks/internal/<str:audiobook_id>/status/', views.get_audiobook_status, name='visual_audiobook_status_internal'),  # GET

    # user-facing (router) routes after internal ones
    path('', include(router.urls)),
]