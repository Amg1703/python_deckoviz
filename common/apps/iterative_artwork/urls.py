from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from .views import IterativeArtworkInternalViewSet, IterativeArtworkIterationInternalViewSet

router = DefaultRouter()
router.register(r'artworks', IterativeArtworkInternalViewSet, basename='artwork')
router.register(r'iterations', IterativeArtworkIterationInternalViewSet, basename='iteration')

urlpatterns = [
    # Standard REST endpoints (CRUD)
    path('artworks/', 
         csrf_exempt(IterativeArtworkInternalViewSet.as_view({
             'get': 'list',
             'post': 'create'
         })),
         name='artwork-list'),
    
    path('artworks/<int:pk>/', 
         csrf_exempt(IterativeArtworkInternalViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         })),
         name='artwork-detail'),
    
    path('iterations/', 
         csrf_exempt(IterativeArtworkIterationInternalViewSet.as_view({
             'get': 'list',
             'post': 'create'
         })),
         name='iteration-list'),
    
    path('iterations/<int:pk>/', 
         csrf_exempt(IterativeArtworkIterationInternalViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         })),
         name='iteration-detail'),
    
    # Custom action endpoints (CSRF exempt)
    path('artworks/link_iterations/', 
         csrf_exempt(IterativeArtworkInternalViewSet.as_view({'post': 'link_iterations'})),
         name='artwork-link-iterations'),
    
    path('iterations/count_unsaved/', 
         csrf_exempt(IterativeArtworkIterationInternalViewSet.as_view({'get': 'count_unsaved'})),
         name='iteration-count-unsaved'),
    
    path('iterations/clear_unsaved/', 
         csrf_exempt(IterativeArtworkIterationInternalViewSet.as_view({'delete': 'clear_unsaved'})),
         name='iteration-clear-unsaved'),
]