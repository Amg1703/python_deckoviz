from django.urls import path
from .views import ModeListView, UserModeDetailView, SessionCreateView, UserModeCollectionRemoveView, UserModeMusicRemoveView

urlpatterns = [
    path('', ModeListView.as_view(), name='mode-list'),
    path('<uuid:mode_id>/', UserModeDetailView.as_view(), name='user-mode-detail'),
    path('<uuid:mode_id>/collections/<uuid:collection_id>/', UserModeCollectionRemoveView.as_view(), name='user-mode-collection-remove'),
    path('sessions/', SessionCreateView.as_view(), name='session-create'),
    # Support both endpoints for backward compatibility and clarity
    path('<uuid:mode_id>/music/<uuid:music_id>/', UserModeMusicRemoveView.as_view(), name='user-mode-music-remove'),
    path('<uuid:mode_id>/audio/<uuid:audio_id>/', UserModeMusicRemoveView.as_view(), name='user-mode-audio-remove'),
]
