from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIModelViewSet, AIOperationViewSet, AICallbackViewSet,
    TranscriptionViewSet, AnalysisViewSet, SummarizationViewSet,
    ImageGenerationViewSet
)

router = DefaultRouter()
router.register(r'models', AIModelViewSet, basename='ai-models')
router.register(r'operations', AIOperationViewSet, basename='ai-operations')
router.register(r'callbacks', AICallbackViewSet, basename='ai-callbacks')

urlpatterns = [
    path('', include(router.urls)),
    path('transcribe/', TranscriptionViewSet.as_view({'post': 'create'}), name='transcribe'),
    path('analyze/', AnalysisViewSet.as_view({'post': 'create'}), name='analyze'),
    path('summarize/', SummarizationViewSet.as_view({'post': 'create'}), name='summarize'),
    path('generate-image/', ImageGenerationViewSet.as_view({'post': 'create'}), name='generate-image'),
    path('webhook/', AICallbackViewSet.as_view({'post': 'webhook'}), name='ai-webhook'),
]
