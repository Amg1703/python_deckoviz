from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Event, EventType, ScheduleType
from .serializers import (
    EventSerializer,
    EventCreateRequestSerializer,
    EventUpdateSerializer,
    EventExecutionUpdateSerializer
)
import logging
import uuid

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([])  # No auth required for internal API calls from FastAPI
def create_event(request):
    """Create a new event record (called from FastAPI)"""
    try:
        serializer = EventCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get user
        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create event
        event = Event.objects.create(
            user=user,
            event_name=data['event_name'],
            event_type=data['event_type'],
            trigger_time=data['trigger_time'],
            trigger_time_local=data.get('trigger_time_local'),
            schedule_type=data['schedule_type'],
            timezone=data.get('timezone', 'UTC'),
            day_of_week=data.get('day_of_week'),
            interval_minutes=data.get('interval_minutes'),
            max_executions=data.get('max_executions'),
            expires_at=data.get('expires_at'),
            visual_config=data['visual_config'],
            location=data.get('location'),
            description=data.get('description'),
            enabled=data.get('enabled', True)
        )
        
        event_serializer = EventSerializer(event)
        
        return Response({
            'success': True,
            'message': 'Event created successfully',
            'data': event_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.exception("Error creating event")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No auth required for internal API calls
def get_event(request, event_id):
    """Get event by ID (called from FastAPI)"""
    try:
        event = get_object_or_404(Event, id=event_id)
        serializer = EventSerializer(event)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error fetching event {event_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No auth required for internal API calls
def list_events(request):
    """List events with optional filters (called from FastAPI)"""
    try:
        user_id = request.GET.get('user_id')
        enabled_only = request.GET.get('enabled_only', 'false').lower() == 'true'
        
        query = Event.objects.all()
        
        if user_id:
            query = query.filter(user__id=user_id)
        
        if enabled_only:
            query = query.filter(enabled=True)
        
        events = query.order_by('-created_at')
        serializer = EventSerializer(events, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Error listing events")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([])  # No auth required for internal API calls
def update_event(request, event_id):
    """Update event fields (called from FastAPI)"""
    try:
        event = get_object_or_404(Event, id=event_id)
        
        serializer = EventUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update fields
        for field, value in serializer.validated_data.items():
            setattr(event, field, value)
        
        event.save()
        
        event_serializer = EventSerializer(event)
        
        return Response({
            'success': True,
            'message': 'Event updated successfully',
            'data': event_serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error updating event {event_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([])  # No auth required for internal API calls
def delete_event(request, event_id):
    """Delete event (called from FastAPI)"""
    try:
        event = get_object_or_404(Event, id=event_id)
        event.delete()
        
        return Response({
            'success': True,
            'message': 'Event deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error deleting event {event_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # No auth required for internal API calls
def update_execution_stats(request, event_id):
    """Update event execution statistics (called from FastAPI)"""
    try:
        event = get_object_or_404(Event, id=event_id)
        
        serializer = EventExecutionUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update execution stats
        event.execution_count += 1
        event.last_execution = timezone.now()
        
        error = serializer.validated_data.get('error')
        if error:
            event.last_error = error
            event.last_error_time = timezone.now()
        
        event.save()
        
        return Response({
            'success': True,
            'message': 'Execution stats updated'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error updating execution stats for event {event_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # No auth required for internal API calls
def enable_event(request, event_id):
    """Enable an event (called from FastAPI)"""
    try:
        event = get_object_or_404(Event, id=event_id)
        event.enabled = True
        event.save()
        
        return Response({
            'success': True,
            'message': 'Event enabled'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error enabling event {event_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([])  # No auth required for internal API calls
def disable_event(request, event_id):
    """Disable an event (called from FastAPI)"""
    try:
        event = get_object_or_404(Event, id=event_id)
        event.enabled = False
        event.save()
        
        return Response({
            'success': True,
            'message': 'Event disabled'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception(f"Error disabling event {event_id}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Requires authentication for user-facing endpoint
def list_user_events(request):
    """List all events for authenticated user (user-facing endpoint)"""
    try:
        user = request.user
        events = Event.objects.filter(user=user).order_by('-created_at')
        
        serializer = EventSerializer(events, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Error listing user events")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])  # No auth required for internal API calls
def check_duplicate_event(request):
    """Check if a duplicate event exists (called from FastAPI)"""
    try:
        user_id = request.GET.get('user_id')
        trigger_time = request.GET.get('trigger_time')
        schedule_type = request.GET.get('schedule_type')
        day_of_week = request.GET.get('day_of_week')
        
        if not all([user_id, trigger_time, schedule_type]):
            return Response({
                'success': False,
                'message': 'Missing required parameters: user_id, trigger_time, schedule_type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build query to find duplicate
        query = Event.objects.filter(
            user__id=user_id,
            trigger_time=trigger_time,
            schedule_type=schedule_type,
            enabled=True
        )
        
        # For weekly events, also check day_of_week
        if schedule_type == 'weekly' and day_of_week:
            query = query.filter(day_of_week=day_of_week)
        
        duplicate = query.first()
        
        if duplicate:
            return Response({
                'success': True,
                'data': {
                    'exists': True,
                    'event_id': str(duplicate.id),
                    'event_name': duplicate.event_name,
                    'trigger_time': duplicate.trigger_time,
                    'schedule_type': duplicate.schedule_type,
                    'day_of_week': duplicate.day_of_week
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': True,
            'data': {'exists': False}
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Error checking duplicate event")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)