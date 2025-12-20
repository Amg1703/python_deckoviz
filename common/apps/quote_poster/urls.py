from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from .views import (
    BackgroundViewSet,
    QuotePosterViewSet,
    PosterFeedbackViewSet,
    PosterShareViewSet,
)

router = DefaultRouter()
router.register(r'backgrounds', BackgroundViewSet, basename='background')
router.register(r'posters', QuotePosterViewSet, basename='quote-poster')
router.register(r'feedback', PosterFeedbackViewSet, basename='poster-feedback')
router.register(r'shares', PosterShareViewSet, basename='poster-share')

urlpatterns = [
    path('', include(router.urls)),
    
    # Internal endpoints for FastAPI - CSRF exempt
    path('internal/backgrounds/create/', 
         csrf_exempt(BackgroundViewSet.as_view({'post': 'create_background'})), 
         name='create-background'),
    path('internal/backgrounds/', 
         BackgroundViewSet.as_view({'get': 'get_background'}), 
         name='get-background'),
    path('internal/backgrounds/update/', 
         csrf_exempt(BackgroundViewSet.as_view({'patch': 'update_background'})), 
         name='update-background'),
    path('internal/backgrounds/delete/', 
         csrf_exempt(BackgroundViewSet.as_view({'delete': 'delete_background'})), 
         name='delete-background'),
    
    path('internal/posters/create/', 
         csrf_exempt(QuotePosterViewSet.as_view({'post': 'create_poster'})), 
         name='create-poster'),
    path('internal/posters/', 
         QuotePosterViewSet.as_view({'get': 'get_poster'}), 
         name='get-poster'),
    path('internal/posters/update/', 
         csrf_exempt(QuotePosterViewSet.as_view({'patch': 'update_poster'})), 
         name='update-poster'),
    path('internal/posters/delete/', 
         csrf_exempt(QuotePosterViewSet.as_view({'delete': 'delete_poster'})), 
         name='delete-poster'),
    
    path('internal/feedback/', 
         csrf_exempt(PosterFeedbackViewSet.as_view({'post': 'submit_feedback'})), 
         name='submit-feedback'),
    path('internal/share/', 
         csrf_exempt(QuotePosterViewSet.as_view({'patch': 'share_poster'})), 
         name='share-poster'),
    
    path('backgrounds/list/', 
         BackgroundViewSet.as_view({'get': 'list_backgrounds'}), 
         name='list-backgrounds'),
    path('posters/list/', 
         QuotePosterViewSet.as_view({'get': 'list_posters'}), 
         name='list-posters'),
    
    path('public/', 
         QuotePosterViewSet.as_view({'get': 'public'}), 
         name='public-poster'),
]