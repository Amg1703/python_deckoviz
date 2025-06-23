from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import Image
from .serializers import ImageSearchSerializer
from django.db.models import Q

class ImageSearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ImageSearchView(ListAPIView):
    serializer_class = ImageSearchSerializer
    pagination_class = ImageSearchPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return Image.objects.none()

        admin_user_id = "8e133332-9565-4451-a296-ab277b037742"
        
        # Ensure metadata is not null and filter by admin user
        queryset = Image.objects.filter(
            uploaded_by_id=admin_user_id,
            metadata__isnull=False
        )

        # Search in title, labels, and descriptions
        search_query = (
            Q(metadata__title__icontains=query) |
            Q(metadata__labels__icontains=query) |
            Q(metadata__descriptions__emotive__icontains=query) |
            Q(metadata__descriptions__literal__icontains=query)
        )
        
        return queryset.filter(search_query) 