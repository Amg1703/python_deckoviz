from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import MusicTask, Lyrics, MusicVideo
from .serializers import (
    MusicTaskSerializer, MusicTaskCreateSerializer, MusicTaskUpdateSerializer,
    LyricsSerializer, LyricsCreateSerializer, LyricsUpdateSerializer,
    MusicVideoSerializer, MusicVideoCreateSerializer, MusicVideoUpdateSerializer
)


class MusicTaskInternalViewSet(viewsets.ModelViewSet):
    """Internal API for MusicTask operations (no authentication)"""
    
    queryset = MusicTask.objects.all()
    serializer_class = MusicTaskSerializer
    lookup_field = 'request_id'
    lookup_url_kwarg = 'request_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MusicTaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MusicTaskUpdateSerializer
        return MusicTaskSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full object
        instance = MusicTask.objects.get(request_id=serializer.data['request_id'])
        output_serializer = MusicTaskSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get all music tasks for a user"""
        tasks = self.queryset.filter(user_id=user_id).order_by('-created_at')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class LyricsInternalViewSet(viewsets.ModelViewSet):
    """Internal API for Lyrics operations (no authentication)"""
    
    queryset = Lyrics.objects.all()
    serializer_class = LyricsSerializer
    lookup_field = 'lyrics_id'
    lookup_url_kwarg = 'lyrics_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LyricsCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LyricsUpdateSerializer
        return LyricsSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full object
        instance = Lyrics.objects.get(lyrics_id=serializer.data['lyrics_id'])
        output_serializer = LyricsSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get all lyrics for a user"""
        lyrics_list = self.queryset.filter(user_id=user_id).order_by('-created_at')
        serializer = self.get_serializer(lyrics_list, many=True)
        return Response(serializer.data)


class MusicVideoInternalViewSet(viewsets.ModelViewSet):
    """Internal API for MusicVideo operations (no authentication)"""
    
    queryset = MusicVideo.objects.all()
    serializer_class = MusicVideoSerializer
    lookup_field = 'video_id'
    lookup_url_kwarg = 'video_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MusicVideoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MusicVideoUpdateSerializer
        return MusicVideoSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full object
        instance = MusicVideo.objects.get(video_id=serializer.data['video_id'])
        output_serializer = MusicVideoSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Get all music videos for a user"""
        videos = self.queryset.filter(user_id=user_id).order_by('-created_at')
        serializer = self.get_serializer(videos, many=True)
        return Response(serializer.data)
