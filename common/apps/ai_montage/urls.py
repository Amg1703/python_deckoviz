from django.urls import path
from . import views

urlpatterns = [
    # Internal API endpoints (called from FastAPI)
    path('internal/create/', views.create_montage, name='ai_montage_create'),
    path('internal/<uuid:montage_id>/', views.get_montage, name='ai_montage_get'),
    path('internal/<uuid:montage_id>/update/', views.update_montage, name='ai_montage_update'),
    path('internal/<uuid:montage_id>/status/', views.get_montage_status, name='ai_montage_status'),
    path('internal/<uuid:montage_id>/link-images/', views.link_images_to_montage, name='ai_montage_link_images'),
    path('internal/images/save/', views.save_uploaded_image, name='ai_montage_save_image'),
    
    # User-facing API endpoints
    path('list/', views.list_user_montages, name='ai_montage_list'),
]
