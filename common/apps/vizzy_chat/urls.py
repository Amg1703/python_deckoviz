"""
Vizzy Chat URL Configuration

RESTful URL routing for Vizzy chat API endpoints
"""
from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    VizzyChatSessionViewSet,
    VizzyChatMessageViewSet,
    VizzyUserProfileView,
    VizzyUserContextView,
    VizzyMoodHistoryViewSet,
    VizzyContextDataViewSet,
)

app_name = 'vizzy_chat'

# Main router for top-level resources
router = routers.DefaultRouter()
router.register(r'sessions', VizzyChatSessionViewSet, basename='session')
router.register(r'mood-history', VizzyMoodHistoryViewSet, basename='mood-history')
router.register(r'context-data', VizzyContextDataViewSet, basename='context-data')

# Nested router for messages within sessions
sessions_router = routers.NestedDefaultRouter(router, r'sessions', lookup='session')
sessions_router.register(r'messages', VizzyChatMessageViewSet, basename='session-messages')

urlpatterns = [
    # Session and nested message routes
    path('', include(router.urls)),
    path('', include(sessions_router.urls)),
    
    # User profile endpoints
    path('profile/', VizzyUserProfileView.as_view(), name='user-profile'),
    
    # User context endpoint (for FastAPI consumption)
    path('users/context/', VizzyUserContextView.as_view(), name='user-context'),
]
