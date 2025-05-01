from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('all', views.ReviewListView, basename='reviews')
router.register('customer-reviews', views.CustomerReviewView, basename='customer_reviews')


urlpatterns = [
    path('', include(router.urls)),
]

 