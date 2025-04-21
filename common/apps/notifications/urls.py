from django.urls import path,include,re_path 
from rest_framework.routers import DefaultRouter 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()


urlpatterns = [
    path('',include(router.urls)),
]
