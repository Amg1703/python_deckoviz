"""
URL configuration for deckoviz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include,re_path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView,SpectacularRedocView,SpectacularSwaggerView


# Set dynamic admin title based on the environment
if settings.DEBUG:
    admin.site.site_header = 'Decoviz Admin (Development)'
    admin.site.site_title = 'Decoviz Admin Portal (Dev)'
else:
    admin.site.site_header = 'Decoviz Admin'
    admin.site.site_title = 'Decoviz Admin Portal'
admin.site.site_url = 'https://deckoviz.com/'


router = DefaultRouter()


urlpatterns = [
    path('admin/', admin.site.urls), 
    
    #authentication api
    path('auth/',include('apps.authentication.urls')),
    
    # gallery api
    path('gallery/', include('apps.gallery.urls')), 
    
    #marketplace api
    path('marketplace/', include('apps.marketplace.urls')),
    
    #orders api
    path('order/', include('apps.orders.urls')),
    
    #payments api
    path('payment/', include('apps.payments.urls')),

    #credits api
    path('credits/', include('apps.credits.urls')),

    # ai integration api
    path('ai/', include('apps.ai_integration.urls')),
     
    #api documentation view
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
