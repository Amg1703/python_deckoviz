from django.urls import path, include
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
from django.views.generic import RedirectView


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
    
    #cart api
    path('carts/', include('apps.carts.urls')),
    
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

    #blogs api
    path('blogs/',include('apps.blogs.urls')),
    
    # metacollections api
    path('metacollections/', include('apps.metacollections.urls')),

    # modes api
    path('modes/', include('apps.modes.urls')),

    # dashboard app
    path('dashboard/', include('apps.dashboard.urls')),

    # metaimages api
    path('metaimages/', include('apps.metaimages.urls')),

    # metaaudios api
    path('metaaudios/', include('apps.metaaudios.urls')),

    # curations api
    path('curations/', include('apps.curations.urls')),

    # analytics api
    path('api/analytics/', include('apps.analytics.urls')),

    # ai_montage api
    path('api/ai-montage/', include('apps.ai_montage.urls')),

    # event_scheduler api
    path('api/event-scheduler/', include('apps.event_scheduler.urls')),

    # collection_with_narration api
    path('api/collection-narration/', include('apps.collection_with_narration.urls')),

    # iterative_artwork api
    path('api/iterative-artwork/', include('apps.iterative_artwork.urls')),

    # market_material api
    # path('api/market-material/', include('apps.market_material.urls')),

    # music_generator api
    path('api/music-generator/', include('apps.music_generator.urls')),

    # visual_chat api
    path('api/visual-chat/', include('apps.visual_chat.urls')),

    # visual_audiobook api
    path('api/visual-audiobook/', include('apps.visual_audiobook.urls')),
    
    # sequential artwork api
    path('api/sequential-artwork/', include('apps.sequential_artwork.urls')),

    # sculpture api
    path('api/sculpture/', include('apps.sculpture.urls')),

    # before_after api
    path('api/before-after/', include('apps.before_after.urls')),

    
    #api documentation view
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/', include('apps.authentication.urls')),

    # social feed api
    path('social/', include('apps.social.urls')),

    # root -> go to the authentication UI/root (auth app)
    # This ensures visiting the site root lands on the auth app instead of falling
    # back to the development static-file handler which produced the 404.
    path('', RedirectView.as_view(url='/auth/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
