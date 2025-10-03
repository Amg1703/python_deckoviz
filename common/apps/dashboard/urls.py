from django.urls import path, re_path
from . import views

app_name = 'dashboard'

# UUID pattern for matching UUID format in URLs
uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

urlpatterns = [
    # Authentication URLs
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Dashboard home view
    path('', views.DashboardHomeView.as_view(), name='home'),
    
    # Collection views
    path('collections/', views.CollectionListView.as_view(), name='collection-list'),
    path('collections/create/', views.CollectionCreateView.as_view(), name='collection-create'),
    re_path(f'collections/(?P<pk>{uuid_pattern})/', views.CollectionDetailView.as_view(), name='collection-detail'),
    re_path(f'collections/(?P<pk>{uuid_pattern})/update/', views.CollectionUpdateView.as_view(), name='collection-update'),
    re_path(f'collections/(?P<pk>{uuid_pattern})/add-images/', views.AddImagesToCollectionView.as_view(), name='add-images'),
    
    # Bulk processing API
    re_path(f'collections/(?P<pk>{uuid_pattern})/process-uploads/', views.ProcessBulkUploadsView.as_view(), name='process-uploads'),
    
    # Create collection with images in one form
    path('collections/create-with-images/', views.CollectionWithImagesCreateView.as_view(), name='collection-with-images-create'),
]
