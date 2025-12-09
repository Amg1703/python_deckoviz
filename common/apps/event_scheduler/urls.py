from django.urls import path
from . import views

urlpatterns = [
    # Internal API endpoints (called from FastAPI)
    path('internal/create/', views.create_event, name='event_create'),
    path('internal/<uuid:event_id>/', views.get_event, name='event_get'),
    path('internal/list/', views.list_events, name='event_list'),
    path('internal/<uuid:event_id>/update/', views.update_event, name='event_update'),
    path('internal/<uuid:event_id>/delete/', views.delete_event, name='event_delete'),
    path('internal/<uuid:event_id>/execution-stats/', views.update_execution_stats, name='event_execution_stats'),
    path('internal/<uuid:event_id>/enable/', views.enable_event, name='event_enable'),
    path('internal/<uuid:event_id>/disable/', views.disable_event, name='event_disable'),
    path('internal/check-duplicate/', views.check_duplicate_event, name='event_check_duplicate'),
    
    # User-facing API endpoints
    path('list/', views.list_user_events, name='event_list_user'),
]
