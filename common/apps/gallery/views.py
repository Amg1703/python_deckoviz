# views.py
from rest_framework import viewsets, filters,mixins
from rest_framework.permissions import IsAuthenticated,AllowAny, IsAdminUser
from .models import Image, Collection, CollectionImage,Audio, DailyCuration, Ritual, DailyImageCuration
from .serializers import (CollectionImageCreateSerializer,AudioSerializer, ImageSerializer, CollectionSerializer, CollectionImageSerializer,CollectionDetailSerializer, DailyCurationSerializer, AdminRitualSerializer, UserRitualSerializer, DailyImageCurationSerializer)
from django.db.models import Q
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from datetime import date
from rest_framework.views import APIView
import requests
import json
import time
import random

class AudioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AudioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['audio']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter audio for current user or active shared audio"""
        return Audio.objects.filter(
            Q(uploaded_by=self.request.user) & Q(is_active=True)
        )
        
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['file']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter images for current user or active shared images"""
        return Image.objects.filter(
            Q(uploaded_by=self.request.user) & Q(is_active=True)
        )
        
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='all-alphabetical')
    def all_alphabetical(self, request):
        """
        Returns all images/artworks in the library in alphabetical order by title.
        """
        queryset = Image.objects.filter(is_active=True).order_by('title')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='admin-images')
    def admin_images(self, request):
        """
        Returns all images uploaded by the admin user (user id 8e133332-9565-4451-a296-ab277b037742) in alphabetical order by title.
        """
        admin_user_id = '8e133332-9565-4451-a296-ab277b037742'
        queryset = Image.objects.filter(uploaded_by_id=admin_user_id, is_active=True).order_by('title')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='public-images')
    def public_images(self, request):
        """
        Returns all public images in random order by using .order_by('?').
        """
        queryset = Image.objects.filter(view='public', is_active=True).order_by('?')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'meta_notes']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectionDetailSerializer
        return CollectionSerializer
    
    def get_queryset(self):
        """Filter collections for current user"""
        return Collection.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """
        Get all public collections that are active, in random order.
        This endpoint is accessible without authentication.
        """
        public_collections = Collection.objects.filter(
            view='public',
            is_active=True
        ).order_by('?')
        
        page = self.paginate_queryset(public_collections)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(public_collections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='attach_music')
    def attach_music(self, request, pk=None):
        """
        Attach or replace a music file for a collection. Only the owner can update.
        """
        collection = self.get_object()
        if collection.user != request.user:
            return Response({'detail': 'Not authorized to modify this collection.'}, status=403)
        music_file = request.FILES.get('music')
        if not music_file:
            return Response({'detail': 'No music file provided.'}, status=400)
        # Replace the music file
        collection.music = music_file
        collection.save(update_fields=['music'])
        return Response({'detail': 'Music file attached successfully.', 'music_url': collection.music.url})


class CollectionImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['POST','PUT']:
            return CollectionImageCreateSerializer
        return CollectionImageSerializer
    
    def get_queryset(self):
        return CollectionImage.objects.filter(collection__user=self.request.user)


class TestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            images = Image.objects.filter(is_active=True)
            batch_size = 100
            for i in range(0, images.count(), batch_size):
                batch = images[i:i+batch_size]
                for image in batch:
                    try:
                        md = image.metadata
                        if isinstance(md, dict) and set(md.keys()) == {"tags", "title", "mood_tags", "description"}:
                            # Skip images with correct metadata format
                            continue
                        url = "https://ai.deckoviz.com/image-meta-gen/generate-from-url"
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgwNDk3MjU3LCJpYXQiOjE3NDg5NjEyNTcsImp0aSI6IjhiZDc5YmMzMjMzZTQwNGJhZDQwOWMxMWIwNDIzZGEyIiwidXNlcl9pZCI6ImNiODYxYjVjLWYwYjEtNGQxNy1hOWM2LTE0MTI0YzhhOTdiYiJ9.t9EuZW5nFwTxTAgFT9LoM8BhPgu377FRrHXus8igA7c"
                        }
                        payload = {
                            "url": image.file.url
                        }
                        print(f"Generating metadata for: {image.file.url}")
                        response = requests.post(url, headers=headers, json=payload, timeout=30)
                        if response.status_code == 200:
                            metadata = response.json().get('metadata', {})
                            image.metadata = metadata
                            image.save()
                            image_identifier = image.title if image.title else image.id
                            metadata_title = metadata.get('title', 'N/A')
                            print(f"Successfully generated metadata for: {image_identifier} - Title: {metadata_title}")
                        else:
                            print(f"Error generating metadata for {image.file.url}: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"Error processing image {image.id}: {str(e)}")
                
                print(f"Processed batch {i//batch_size + 1}")
                time.sleep(1) # Sleep for 1 second between batches

            return Response({"message": "Metadata generation process completed."})
        except Exception as e:
            return Response({"message": str(e)})

@api_view(['GET'])
@permission_classes([AllowAny])
def today_curation(request):
    today = date.today()
    try:
        curation = DailyCuration.objects.get(date=today)
        data = DailyCurationSerializer(curation, context={'request': request}).data
        return Response(data)
    except DailyCuration.DoesNotExist:
        return Response({'date': str(today), 'collections': []})

@api_view(['GET'])
@permission_classes([AllowAny])
def today_image_curation(request):
    today = date.today()
    try:
        curation = DailyImageCuration.objects.get(date=today)
        data = DailyImageCurationSerializer(curation, context={'request': request}).data
        return Response(data)
    except DailyImageCuration.DoesNotExist:
        return Response({'date': str(today), 'images': []})

class AdminRitualViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminRitualSerializer
    queryset = Ritual.objects.filter(is_global=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['time_of_day', 'name']
    ordering = ['time_of_day']

    @action(detail=False, methods=['get'], url_path='by-time', permission_classes=[IsAdminUser])
    def by_time(self, request):
        time_str = request.query_params.get('time')
        if not time_str:
            return Response({'detail': 'Missing time parameter.'}, status=400)
        rituals = Ritual.objects.filter(is_global=True, time_of_day=time_str, is_active=True)
        data = []
        for ritual in rituals:
            collections = list(ritual.collections.all())
            random.shuffle(collections)
            data.append({
                'id': ritual.id,
                'name': ritual.name,
                'time_of_day': ritual.time_of_day,
                'collections': CollectionSerializer(collections, many=True).data
            })
        return Response(data)

class UserRitualViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserRitualSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['time_of_day', 'name']
    ordering = ['time_of_day']

    def get_queryset(self):
        return Ritual.objects.filter(is_global=False, created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'], url_path='by-time', permission_classes=[IsAuthenticated])
    def by_time(self, request):
        time_str = request.query_params.get('time')
        if not time_str:
            return Response({'detail': 'Missing time parameter.'}, status=400)
        rituals = Ritual.objects.filter(is_global=False, created_by=request.user, time_of_day=time_str, is_active=True)
        data = []
        for ritual in rituals:
            collections = list(ritual.collections.all())
            random.shuffle(collections)
            data.append({
                'id': ritual.id,
                'name': ritual.name,
                'time_of_day': ritual.time_of_day,
                'collections': CollectionSerializer(collections, many=True).data
            })
        return Response(data)
