from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Internal API endpoints (no authentication required for FastAPI communication)
internal_patterns = [
    path('start-usage/', views.start_usage_tracking, name='start_usage_tracking'),
    path('complete-usage/', views.complete_usage_tracking, name='complete_usage_tracking'),
    path('fail-usage/', views.fail_usage_tracking, name='fail_usage_tracking'),
]

# User-facing API endpoints (authentication required)
user_patterns = [
    path('usage-history/', views.UserFeatureUsageListView.as_view(), name='user_usage_history'),
    path('usage-summary/', views.UserUsageSummaryView.as_view(), name='user_usage_summary'),
    path('sessions/', views.UserSessionListView.as_view(), name='user_sessions'),
    path('sessions/create/', views.create_user_session, name='create_user_session'),
    path('sessions/<str:session_id>/end/', views.end_user_session, name='end_user_session'),
    path('daily-stats/', views.DailyStatsListView.as_view(), name='user_daily_stats'),
    path('pricing/', views.FeaturePricingListView.as_view(), name='feature_pricing'),
    path('feature-cost/<str:feature_name>/', views.get_feature_cost, name='get_feature_cost'),
]

# Admin endpoints
admin_patterns = [
    path('platform-analytics/', views.platform_analytics, name='platform_analytics'),
]

urlpatterns = [
    # Internal API (for FastAPI communication)
    path('internal/', include(internal_patterns)),
    
    # User API
    path('user/', include(user_patterns)),
    
    # Admin API
    path('admin/', include(admin_patterns)),
]
