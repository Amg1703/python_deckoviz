from django.urls import path
from .views import ModeListView, UserModeDetailView, SessionCreateView, UserModeCollectionRemoveView

urlpatterns = [
    path('', ModeListView.as_view(), name='mode-list'),
    path('<uuid:mode_id>/', UserModeDetailView.as_view(), name='user-mode-detail'),
    path('<uuid:mode_id>/collections/<uuid:collection_id>/', UserModeCollectionRemoveView.as_view(), name='user-mode-collection-remove'),
    path('sessions/', SessionCreateView.as_view(), name='session-create'),
]
