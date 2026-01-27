"""
Vizzy Chat REST API Views

Production-ready views with:
- Proper authentication and permissions
- Query optimization
- Error handling
- Rate limiting support
- Clean separation of concerns
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import (
    VizzyChatSession,
    VizzyChatMessage,
    VizzyUserProfile,
    VizzyMoodHistory,
    VizzyContextData
)
from .serializers import (
    VizzyChatSessionListSerializer,
    VizzyChatSessionDetailSerializer,
    VizzyChatSessionCreateSerializer,
    VizzyChatMessageSerializer,
    VizzyChatMessageCreateSerializer,
    VizzyUserProfileSerializer,
    VizzyMoodHistorySerializer,
    VizzyMoodHistoryCreateSerializer,
    VizzyContextDataSerializer,
    VizzyContextDataCreateSerializer,
    VizzyUserContextSerializer,
)
from .services import (
    VizzySessionService,
    VizzyMessageService,
    VizzyUserContextService,
    VizzyMoodService,
    VizzyContextService,
)


class StandardResultPagination(PageNumberPagination):
    """Standard pagination for list views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(tags=['Vizzy Chat - Sessions'])
class VizzyChatSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Vizzy chat sessions
    
    Provides CRUD operations for chat sessions with optimized queries
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return VizzyChatSessionListSerializer
        elif self.action == 'create':
            return VizzyChatSessionCreateSerializer
        return VizzyChatSessionDetailSerializer
    
    def get_queryset(self):
        """
        Get sessions for authenticated user
        
        Optimized with select_related and prefetch_related
        """
        user = self.request.user
        active_only = self.request.query_params.get('active_only', 'true').lower() == 'true'
        
        qs = VizzyChatSession.objects.filter(user=user).select_related('user')
        
        if active_only:
            qs = qs.filter(is_active=True)
        
        return qs.order_by('-updated_at')
    
    @extend_schema(
        summary="List user's chat sessions",
        parameters=[
            OpenApiParameter(
                name='active_only',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter to only active sessions (default: true)'
            ),
        ],
        responses={200: VizzyChatSessionListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all sessions for authenticated user"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get session details with messages",
        responses={
            200: VizzyChatSessionDetailSerializer,
            404: OpenApiResponse(description='Session not found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get detailed session with messages"""
        import logging
        logger = logging.getLogger(__name__)
        
        session_id = kwargs.get('pk')
        
        try:
            message_limit = int(request.query_params.get('message_limit', 100))
        except (ValueError, TypeError):
            message_limit = 100
        
        try:
            session = VizzySessionService.get_session_with_messages(
                session_id=session_id,
                message_limit=message_limit
            )
            
            if not session:
                return Response(
                    {'detail': 'Session not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if session.user != request.user:
                return Response(
                    {'detail': 'You do not have permission to access this session'},
                    status=status.HTTP_404_NOT_FOUND  # Return 404 instead of 403 for security
                )
            
            serializer = self.get_serializer(session, context={'message_limit': message_limit})
            return Response(serializer.data)
            
        except VizzyChatSession.DoesNotExist:
            return Response(
                {'detail': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}", exc_info=True)
            return Response(
                {'detail': 'Internal server error retrieving session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Create new chat session",
        request=VizzyChatSessionCreateSerializer,
        responses={
            201: VizzyChatSessionDetailSerializer,
            400: OpenApiResponse(description='Invalid input')
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new chat session"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        session = VizzySessionService.create_session(
            user=request.user,
            mode=serializer.validated_data.get('mode', 'home'),
            title=serializer.validated_data.get('title')
        )
        
        output_serializer = VizzyChatSessionDetailSerializer(session)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Update session (title, mode)",
        request=VizzyChatSessionCreateSerializer,
        responses={
            200: VizzyChatSessionDetailSerializer,
            404: OpenApiResponse(description='Session not found')
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a session"""
        instance = self.get_object()
        
        if instance.user != request.user:
            return Response(
                {'detail': 'You do not have permission to update this session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = VizzyChatSessionCreateSerializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        output_serializer = VizzyChatSessionDetailSerializer(instance)
        return Response(output_serializer.data)
    
    @extend_schema(
        summary="Close a chat session",
        responses={
            200: OpenApiResponse(description='Session closed successfully'),
            404: OpenApiResponse(description='Session not found')
        }
    )
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a chat session"""
        # Fetch session without is_active filter to handle already-closed sessions
        session = get_object_or_404(VizzyChatSession, id=pk, user=request.user)
        
        if not session.is_active:
            # Session already closed - return success message
            serializer = VizzyChatSessionDetailSerializer(session)
            return Response({
                'status': 'success',
                'message': 'Session already closed',
                'session': serializer.data
            })
        
        # Close the active session
        closed_session = VizzySessionService.close_session(session_id=str(session.id))
        
        serializer = VizzyChatSessionDetailSerializer(closed_session)
        return Response({
            'status': 'success',
            'message': 'Session closed successfully',
            'session': serializer.data
        })
    
    @extend_schema(
        summary="Delete a chat session",
        responses={
            204: OpenApiResponse(description='Session deleted successfully'),
            404: OpenApiResponse(description='Session not found')
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a session (soft delete by closing)"""
        instance = self.get_object()
        
        if instance.user != request.user:
            return Response(
                {'detail': 'You do not have permission to delete this session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete by closing instead of hard delete
        VizzySessionService.close_session(session_id=str(instance.id))
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Vizzy Chat - Messages'])
class VizzyChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages
    
    Messages are always associated with a session
    Messages are immutable once created (audit trail)
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultPagination
    http_method_names = ['get', 'post', 'head', 'options']  # No PUT, PATCH, DELETE
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return VizzyChatMessageCreateSerializer
        return VizzyChatMessageSerializer
    
    def get_queryset(self):
        """Get messages for a specific session"""
        session_id = self.kwargs.get('session_pk')
        
        # Verify session exists and belongs to user
        session = get_object_or_404(
            VizzyChatSession,
            id=session_id,
            user=self.request.user
        )
        
        return VizzyChatMessage.objects.filter(
            session=session
        ).select_related('session', 'session__user').order_by('created_at')
    
    @extend_schema(
        summary="List messages in a session",
        responses={200: VizzyChatMessageSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all messages in a session"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get specific message",
        responses={
            200: VizzyChatMessageSerializer,
            404: OpenApiResponse(description='Message not found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Get a specific message"""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create new message in session",
        request=VizzyChatMessageCreateSerializer,
        responses={
            201: VizzyChatMessageSerializer,
            400: OpenApiResponse(description='Invalid input'),
            404: OpenApiResponse(description='Session not found')
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new message in a session"""
        session_id = self.kwargs.get('session_pk')
        
        # Verify session exists and belongs to user
        session = get_object_or_404(
            VizzyChatSession,
            id=session_id,
            user=request.user
        )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = VizzyMessageService.create_message(
            session_id=str(session.id),
            role=serializer.validated_data['role'],
            content=serializer.validated_data['content'],
            has_images=serializer.validated_data.get('has_images', False),
            image_urls=serializer.validated_data.get('image_urls'),
            detected_emotion=serializer.validated_data.get('detected_emotion'),
            mood_valence=serializer.validated_data.get('mood_valence'),
            mood_arousal=serializer.validated_data.get('mood_arousal'),
            tokens_used=serializer.validated_data.get('tokens_used'),
            processing_time_ms=serializer.validated_data.get('processing_time_ms')
        )
        
        output_serializer = VizzyChatMessageSerializer(message)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Vizzy Chat - User Profile'])
class VizzyUserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for managing user's Vizzy profile
    
    Provides read and update operations for user profile
    """
    serializer_class = VizzyUserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create profile for authenticated user"""
        profile, _ = VizzyUserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    @extend_schema(
        summary="Get user's Vizzy profile",
        responses={200: VizzyUserProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        """Get user profile"""
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user's Vizzy profile",
        request=VizzyUserProfileSerializer,
        responses={
            200: VizzyUserProfileSerializer,
            400: OpenApiResponse(description='Invalid input')
        }
    )
    def patch(self, request, *args, **kwargs):
        """Partially update user profile"""
        profile = self.get_object()
        
        # Use serializer for validation
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


@extend_schema(tags=['Vizzy Chat - User Context'])
class VizzyUserContextView(generics.GenericAPIView):
    """
    View for retrieving comprehensive user context
    
    Used by FastAPI service to get all context for AI processing
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VizzyUserContextSerializer
    
    @extend_schema(
        summary="Get comprehensive user context for AI",
        responses={200: VizzyUserContextSerializer}
    )
    def get(self, request):
        """Get comprehensive user context"""
        use_cache = request.query_params.get('use_cache', 'true').lower() == 'true'
        
        context = VizzyUserContextService.get_user_context(
            user=request.user,
            use_cache=use_cache
        )
        
        return Response(context)


@extend_schema(tags=['Vizzy Chat - Mood History'])
class VizzyMoodHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for mood history tracking
    
    Provides operations for recording and retrieving mood data
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return VizzyMoodHistoryCreateSerializer
        return VizzyMoodHistorySerializer
    
    def get_queryset(self):
        """Get mood history for authenticated user"""
        days = int(self.request.query_params.get('days', 30))
        return VizzyMoodHistory.objects.user_mood_timeline(
            self.request.user,
            days=days
        ).select_related('user', 'session')
    
    @extend_schema(
        summary="Get user's mood history",
        parameters=[
            OpenApiParameter(
                name='days',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of days to look back (default: 30)'
            ),
        ],
        responses={200: VizzyMoodHistorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List mood history"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Record new mood entry",
        request=VizzyMoodHistoryCreateSerializer,
        responses={
            201: VizzyMoodHistorySerializer,
            400: OpenApiResponse(description='Invalid input')
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new mood entry"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        mood_entry = VizzyMoodService.record_mood(
            user=request.user,
            valence=serializer.validated_data['valence'],
            arousal=serializer.validated_data['arousal'],
            emotion_label=serializer.validated_data['emotion_label'],
            source=serializer.validated_data['source'],
            session_id=str(serializer.validated_data['session'].id) if serializer.validated_data.get('session') else None,
            confidence=serializer.validated_data.get('confidence')
        )
        
        output_serializer = VizzyMoodHistorySerializer(mood_entry)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Get mood pattern analysis",
        responses={200: OpenApiResponse(description='Mood pattern analysis')}
    )
    @action(detail=False, methods=['get'])
    def analyze(self, request):
        """Get mood pattern analysis for user"""
        analysis = VizzyMoodService.analyze_mood_patterns(request.user)
        return Response(analysis)


@extend_schema(tags=['Vizzy Chat - Context Data'])
class VizzyContextDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing context data
    
    Provides CRUD operations for user context entries
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return VizzyContextDataCreateSerializer
        return VizzyContextDataSerializer
    
    def get_queryset(self):
        """Get context data for authenticated user"""
        qs = VizzyContextData.objects.filter(user=self.request.user).select_related('user')
        
        # Filter by context_type if provided
        context_type = self.request.query_params.get('context_type')
        if context_type:
            qs = qs.filter(context_type=context_type)
        
        return qs.order_by('-access_count', '-accessed_at')
    
    @extend_schema(
        summary="List user's context data",
        parameters=[
            OpenApiParameter(
                name='context_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by context type'
            ),
        ],
        responses={200: VizzyContextDataSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List context data"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get specific context entry",
        responses={
            200: VizzyContextDataSerializer,
            404: OpenApiResponse(description='Context not found')
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve context data and increment access count"""
        from django.db.models import F
        from django.utils import timezone
        
        instance = self.get_object()
        
        # Increment access count
        instance.access_count = F('access_count') + 1
        instance.accessed_at = timezone.now()
        instance.save(update_fields=['access_count', 'accessed_at'])
        
        # Refresh to get actual value instead of F() expression
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Create new context entry",
        request=VizzyContextDataCreateSerializer,
        responses={
            201: VizzyContextDataSerializer,
            400: OpenApiResponse(description='Invalid input')
        }
    )
    def create(self, request, *args, **kwargs):
        """Create new context data"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        context_data = VizzyContextService.set_context(
            user=request.user,
            context_type=serializer.validated_data['context_type'],
            key=serializer.validated_data['key'],
            value=serializer.validated_data['value']
        )
        
        output_serializer = VizzyContextDataSerializer(context_data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Delete context entry",
        responses={
            204: OpenApiResponse(description='Context deleted successfully'),
            404: OpenApiResponse(description='Context not found')
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete context data"""
        instance = self.get_object()
        
        if instance.user != request.user:
            return Response(
                {'detail': 'You do not have permission to delete this context'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        VizzyContextService.delete_context(
            user=request.user,
            context_id=str(instance.id)
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
