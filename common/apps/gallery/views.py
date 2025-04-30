# views.py
from rest_framework import viewsets, filters,mixins
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Image, Collection, CollectionImage,Audio
from .serializers import (CollectionImageCreateSerializer,AudioSerializer, ImageSerializer, CollectionSerializer, CollectionImageSerializer,CollectionDetailSerializer)
from django.db.models import Q

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


class CollectionImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['POST','PUT']:
            return CollectionImageCreateSerializer
        return CollectionImageSerializer
    
    def get_queryset(self):
        return CollectionImage.objects.filter(collection__user=self.request.user)


from rest_framework.views import APIView
from rest_framework.response import Response
from apps.utils.decoviz_ai import AIClient
from .models import Audio
from apps.utils.storage import Storage

class TestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("Fetching audios to process")
        audios = Audio.objects.filter(transcript_status='processing', is_active=True)
        print(f"Found {audios.count()} audios to process")
        
        for audio in audios:
            try:
                client = AIClient()
                result = client.transcribe_audio(audio.audio.url)
                print(f"Transcribing audio {audio.id}: {result}")

                # Upload transcript to GCS
                storage = Storage()
                upload_response = storage.upload_transcript(result['transcript'], audio.id)
                print(f"Transcript uploaded to {upload_response}")

                # Update audio model
                if result['success']:
                    audio.transcript = result['transcript']
                    audio.transcript_url = upload_response
                    audio.transcript_status = 'completed'
                    audio.save()
                else:
                    print(f"Failed to transcribe audio {audio.id}: {result['error']}")
            except Exception as e:
                print(f"Error processing audio {audio.id}: {str(e)}")
        return Response({"message": "Hello World"})
