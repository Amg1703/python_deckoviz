from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import logging
import secrets
import uuid
from django.utils import timezone
from datetime import timedelta

from .models import Background, QuotePoster, PosterFeedback, PosterShare
from .serializers import (
    BackgroundSerializer,
    QuotePosterSerializer,
    QuotePosterDetailSerializer,
    PosterFeedbackSerializer,
    PosterShareSerializer,
    BackgroundCreateSerializer,
    QuotePosterCreateSerializer,
)

logger = logging.getLogger(__name__)


class BackgroundViewSet(viewsets.ModelViewSet):
    """ViewSet for Background images"""
    serializer_class = BackgroundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'service', 'is_public']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    search_fields = ['prompt', 'session_id']
    
    def get_queryset(self):
        """Return backgrounds for current user"""
        return Background.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user on creation"""
        serializer.save(user=self.request.user)
    
    
    @action(detail=False, methods=['post'])
    def create_background(self, request):
        """Internal endpoint for FastAPI to create background records"""
        serializer = BackgroundCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                background = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Background created successfully",
                        "data": BackgroundSerializer(background).data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"Error creating background: {e}")
                return Response(
                    {
                        "success": False,
                        "message": str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {
                "success": False,
                "message": "Validation error",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def list_backgrounds(self, request):
        """List all backgrounds for current user"""
        queryset = self.get_queryset()
        skip = request.query_params.get('skip', 0)
        limit = request.query_params.get('limit', 20)
        
        try:
            skip = int(skip)
            limit = int(limit)
        except ValueError:
            skip = 0
            limit = 20
        
        total = queryset.count()
        backgrounds = queryset[skip:skip+limit]
        
        return Response(
            {
                "success": True,
                "total": total,
                "skip": skip,
                "limit": limit,
                "data": BackgroundSerializer(backgrounds, many=True).data
            }
        )
    
    @action(detail=False, methods=['get'])
    def backgrounds(self, request):
        """Internal endpoint for FastAPI to list backgrounds"""
        user_id = request.query_params.get('user_id')
        skip = request.query_params.get('skip', 0)
        limit = request.query_params.get('limit', 20)
        
        try:
            skip = int(skip)
            limit = int(limit)
        except ValueError:
            skip = 0
            limit = 20
        
        try:
            user = User.objects.get(id=user_id)
            queryset = Background.objects.filter(user=user)
            total = queryset.count()
            backgrounds = queryset[skip:skip+limit]
            
            return Response(
                {
                    "success": True,
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "data": BackgroundSerializer(backgrounds, many=True).data
                }
            )
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def get_background(self, request):
        """Internal endpoint to get specific background by session_id"""
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            background = Background.objects.get(session_id=session_id)
            return Response(
                {
                    "success": True,
                    "data": BackgroundSerializer(background).data
                }
            )
        except Background.DoesNotExist:
            return Response(
                {"success": False, "message": "Background not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'])
    def update_background(self, request):
        """Internal endpoint to update background"""
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            background = Background.objects.get(session_id=session_id)
            serializer = BackgroundSerializer(background, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Background updated",
                        "data": serializer.data
                    }
                )
            
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Background.DoesNotExist:
            return Response(
                {"success": False, "message": "Background not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'])
    def delete_background(self, request):
        """Internal endpoint to delete background"""
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            background = Background.objects.get(session_id=session_id)
            background.delete()
            
            return Response(
                {"success": True, "message": "Background deleted"}
            )
        except Background.DoesNotExist:
            return Response(
                {"success": False, "message": "Background not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class QuotePosterViewSet(viewsets.ModelViewSet):
    """ViewSet for Quote Posters"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'is_public']
    ordering_fields = ['created_at', 'updated_at', 'share_count']
    ordering = ['-created_at']
    search_fields = ['quote_text', 'session_id']
    
    def get_serializer_class(self):
        """Use detail serializer for retrieve"""
        if self.action == 'retrieve':
            return QuotePosterDetailSerializer
        return QuotePosterSerializer
    
    def get_queryset(self):
        """Return posters for current user"""
        return QuotePoster.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user on creation"""
        serializer.save(user=self.request.user)
        
    
    @action(detail=False, methods=['post'])
    def create_poster(self, request):
        """Internal endpoint for FastAPI to create poster records"""
        serializer = QuotePosterCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                poster = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Poster created successfully",
                        "data": QuotePosterSerializer(poster).data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"Error creating poster: {e}")
                return Response(
                    {
                        "success": False,
                        "message": str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {
                "success": False,
                "message": "Validation error",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def list_posters(self, request):
        """Internal endpoint for FastAPI to list posters"""
        user_id = request.query_params.get('user_id')
        skip = request.query_params.get('skip', 0)
        limit = request.query_params.get('limit', 20)
        
        try:
            skip = int(skip)
            limit = int(limit)
        except ValueError:
            skip = 0
            limit = 20
        
        try:
            user = User.objects.get(id=user_id)
            queryset = QuotePoster.objects.filter(user=user)
            total = queryset.count()
            posters = queryset[skip:skip+limit]
            
            return Response(
                {
                    "success": True,
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "data": QuotePosterSerializer(posters, many=True).data
                }
            )
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def get_poster(self, request):
        """Internal endpoint to get specific poster by session_id"""
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            poster = QuotePoster.objects.get(session_id=session_id)
            return Response(
                {
                    "success": True,
                    "data": QuotePosterDetailSerializer(poster).data
                }
            )
        except QuotePoster.DoesNotExist:
            return Response(
                {"success": False, "message": "Poster not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
    
    @action(detail=False, methods=['patch'])
    def update_poster(self, request):
        """Internal endpoint to update poster"""
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            poster = QuotePoster.objects.get(session_id=session_id)
            serializer = QuotePosterSerializer(poster, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Poster updated",
                        "data": serializer.data
                    }
                )
            
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except QuotePoster.DoesNotExist:
            return Response(
                {"success": False, "message": "Poster not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    
    @action(detail=False, methods=['delete'])
    def delete_poster(self, request):
        """Internal endpoint to delete poster"""
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            poster = QuotePoster.objects.get(session_id=session_id)
            poster.delete()
            
            return Response(
                {"success": True, "message": "Poster deleted"}
            )
        except QuotePoster.DoesNotExist:
            return Response(
                {"success": False, "message": "Poster not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a poster"""
        poster = self.get_object()
        
        if poster.user != request.user:
            return Response(
                {"message": "Cannot share poster"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            share_token = secrets.token_urlsafe(32)
            share = PosterShare.objects.create(
                poster=poster,
                shared_by=request.user,
                share_token=share_token,
                share_url=f"/api/quote-posters/public/{share_token}/"
            )
            
            return Response(
                {
                    "success": True,
                    "data": PosterShareSerializer(share).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error sharing poster: {e}")
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    
    @action(detail=False, methods=['patch'])
    def share_poster(self, request):
        """Internal endpoint to mark poster as shared"""
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            poster = QuotePoster.objects.get(session_id=session_id)
            
            share_token = secrets.token_urlsafe(32)
            share = PosterShare.objects.create(
                poster=poster,
                shared_by=poster.user,
                share_token=share_token,
                share_url=f"/api/quote-posters/public/{share_token}/"
            )
            
            poster.is_public = True
            poster.save(update_fields=['is_public'])
            
            return Response(
                {
                    "success": True,
                    "message": "Poster shared",
                    "data": PosterShareSerializer(share).data
                }
            )
        except QuotePoster.DoesNotExist:
            return Response(
                {"success": False, "message": "Poster not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """Get publicly shared poster"""
        share_token = request.query_params.get('session_id')
        
        if not share_token:
            return Response(
                {"success": False, "message": "share_token required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            share = PosterShare.objects.get(share_token=share_token)
            
            if not share.is_active or share.is_expired():
                return Response(
                    {"success": False, "message": "Share link expired"},
                    status=status.HTTP_410_GONE
                )
            
            share.increment_view_count()
            poster = share.poster
            
            return Response(
                {
                    "success": True,
                    "data": QuotePosterDetailSerializer(poster).data
                }
            )
        except PosterShare.DoesNotExist:
            return Response(
                {"success": False, "message": "Share not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class PosterFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for Poster Feedback"""
    serializer_class = PosterFeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return feedback for posters of current user"""
        return PosterFeedback.objects.filter(poster__user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user on creation"""
        serializer.save(user=self.request.user)
    
    
    @action(detail=False, methods=['post'])
    def submit_feedback(self, request):
        """Internal endpoint to submit feedback"""
        session_id = request.data.get('session_id')
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        
        if not session_id:
            return Response(
                {"success": False, "message": "session_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            poster = QuotePoster.objects.get(session_id=session_id)
            
            feedback, created = PosterFeedback.objects.update_or_create(
                poster=poster,
                user_id=request.user.id if hasattr(request.user, 'id') else None,
                defaults={'rating': rating, 'comment': comment}
            )
            
            return Response(
                {
                    "success": True,
                    "message": "Feedback submitted",
                    "data": PosterFeedbackSerializer(feedback).data
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except QuotePoster.DoesNotExist:
            return Response(
                {"success": False, "message": "Poster not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class PosterShareViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Poster Shares"""
    serializer_class = PosterShareSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return shares created by current user"""
        return PosterShare.objects.filter(shared_by=self.request.user)