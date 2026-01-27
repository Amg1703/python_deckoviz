"""
Vizzy Chat Business Logic Services

Encapsulates complex business logic separate from views.
Provides reusable, testable service functions for:
- Session management
- Message processing
- User context aggregation
- Mood analysis
- Performance optimizations
"""
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .models import (
    VizzyChatSession,
    VizzyChatMessage,
    VizzyUserProfile,
    VizzyMoodHistory,
    VizzyContextData
)

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser as User
else:
    User = get_user_model()


class VizzySessionService:
    """Service for managing chat sessions"""
    
    @staticmethod
    @transaction.atomic
    def create_session(user: User, mode: str = 'home', title: Optional[str] = None) -> VizzyChatSession:
        """
        Create a new chat session for user
        
        Args:
            user: User creating the session
            mode: Session mode ('home' or 'enterprise')
            title: Optional session title
        
        Returns:
            VizzyChatSession: Created session
        """
        # Create session
        session = VizzyChatSession.objects.create(
            user=user,
            mode=mode,
            title=title
        )
        
        # Update or create user profile
        profile, created = VizzyUserProfile.objects.get_or_create(user=user)
        profile.update_engagement(session_created=True)
        
        return session
    
    @staticmethod
    def get_user_sessions(
        user: User,
        active_only: bool = True,
        limit: int = 20
    ) -> List[VizzyChatSession]:
        """
        Get sessions for a user
        
        Args:
            user: User to get sessions for
            active_only: Only return active sessions
            limit: Maximum number of sessions to return
        
        Returns:
            List of VizzyChatSession objects
        """
        sessions = VizzyChatSession.objects.user_sessions(user, active_only=active_only)
        return list(sessions[:limit])
    
    @staticmethod
    @transaction.atomic
    def close_session(session_id: str) -> VizzyChatSession:
        """
        Close a chat session
        
        Args:
            session_id: UUID of session to close
        
        Returns:
            Updated VizzyChatSession
        """
        session = VizzyChatSession.objects.get(id=session_id)
        session.close()
        
        # Invalidate cache
        cache_key = f"vizzy:session:{session_id}:state"
        cache.delete(cache_key)
        
        return session
    
    @staticmethod
    def get_session_with_messages(
        session_id: str,
        message_limit: int = 100
    ) -> Optional[VizzyChatSession]:
        """
        Get session with prefetched messages
        
        Args:
            session_id: UUID of session
            message_limit: Maximum number of messages to fetch
        
        Returns:
            VizzyChatSession with messages or None
        """
        try:
            from django.db.models import Prefetch
            
            # Don't slice queryset in Prefetch - Django doesn't allow it
            # Just prefetch all messages ordered by created_at
            # The serializer will handle limiting based on message_limit
            messages_queryset = VizzyChatMessage.objects.order_by('created_at')
            
            session = VizzyChatSession.objects.select_related('user').prefetch_related(
                Prefetch('messages', queryset=messages_queryset)
            ).get(id=session_id)
            
            return session
        except VizzyChatSession.DoesNotExist:
            return None


class VizzyMessageService:
    """Service for managing chat messages"""
    
    @staticmethod
    @transaction.atomic
    def create_message(
        session_id: str,
        role: str,
        content: str,
        has_images: bool = False,
        image_urls: Optional[List[str]] = None,
        detected_emotion: Optional[str] = None,
        mood_valence: Optional[float] = None,
        mood_arousal: Optional[float] = None,
        tokens_used: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ) -> VizzyChatMessage:
        """
        Create a new message in a session
        
        Args:
            session_id: UUID of parent session
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            has_images: Whether message contains images
            image_urls: List of image URLs
            detected_emotion: Detected emotion label
            mood_valence: Emotional valence (-1 to 1)
            mood_arousal: Emotional arousal (-1 to 1)
            tokens_used: LLM tokens consumed
            processing_time_ms: Processing time in milliseconds
        
        Returns:
            Created VizzyChatMessage
        """
        session = VizzyChatSession.objects.get(id=session_id)
        
        message = VizzyChatMessage.objects.create(
            session=session,
            role=role,
            content=content,
            has_images=has_images,
            image_urls=image_urls or [],
            detected_emotion=detected_emotion,
            mood_valence=mood_valence,
            mood_arousal=mood_arousal,
            tokens_used=tokens_used,
            processing_time_ms=processing_time_ms
        )
        
        # Update user profile if user message
        if role == 'user':
            profile, _ = VizzyUserProfile.objects.get_or_create(user=session.user)
            profile.update_engagement(message_sent=True)
        
        # Invalidate conversation buffer cache
        cache_key = f"vizzy:session:{session_id}:messages"
        cache.delete(cache_key)
        
        return message
    
    @staticmethod
    def get_conversation_history(
        session_id: str,
        limit: int = 50,
        use_cache: bool = True
    ) -> List[VizzyChatMessage]:
        """
        Get conversation history for a session
        
        Args:
            session_id: UUID of session
            limit: Maximum number of messages
            use_cache: Whether to use cache
        
        Returns:
            List of VizzyChatMessage objects
        """
        cache_key = f"vizzy:session:{session_id}:messages:{limit}"
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        messages = list(
            VizzyChatMessage.objects.session_history(
                VizzyChatSession.objects.get(id=session_id),
                limit=limit
            )
        )
        
        if use_cache:
            # Cache for 30 minutes
            cache.set(cache_key, messages, timeout=1800)
        
        return messages


class VizzyUserContextService:
    """Service for aggregating and managing user context"""
    
    @staticmethod
    def get_user_context(user: User, use_cache: bool = True) -> Dict:
        """
        Get comprehensive user context for AI processing
        
        Args:
            user: User to get context for
            use_cache: Whether to use cached data
        
        Returns:
            Dictionary with user context data
        """
        cache_key = f"vizzy:user:{user.id}:profile"
        
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                return cached
        
        # Get or create profile
        profile, _ = VizzyUserProfile.objects.get_or_create(user=user)
        
        # Get recent moods (last 10)
        recent_moods = list(
            VizzyMoodHistory.objects.recent_user_mood(user, limit=10).values(
                'valence', 'arousal', 'emotion_label', 'timestamp', 'source'
            )
        )
        
        # Get context entries (most accessed)
        context_entries = list(
            VizzyContextData.objects.user_context(user).order_by('-access_count')[:20].values(
                'context_type', 'key', 'value', 'access_count'
            )
        )
        
        # Calculate average mood (last 7 days)
        avg_valence = VizzyMoodHistory.objects.average_valence(user, days=7)
        
        context = {
            'user_id': str(user.id),
            'email': user.email,
            'aesthetic_palette': profile.aesthetic_palette,
            'mood_map': profile.mood_map,
            'story_markers': profile.story_markers,
            'device_context': profile.device_context,
            'recent_moods': recent_moods,
            'average_mood_valence': avg_valence,
            'total_sessions': profile.total_sessions,
            'total_messages': profile.total_messages,
            'last_active': profile.last_active.isoformat() if profile.last_active else None,
            'context_entries': context_entries,
        }
        
        if use_cache:
            # Cache for 6 hours
            cache.set(cache_key, context, timeout=21600)
        
        return context
    
    @staticmethod
    @transaction.atomic
    def update_user_profile(
        user: User,
        aesthetic_palette: Optional[Dict] = None,
        mood_map: Optional[Dict] = None,
        story_markers: Optional[List] = None,
        device_context: Optional[Dict] = None
    ) -> VizzyUserProfile:
        """
        Update user profile data
        
        Args:
            user: User to update
            aesthetic_palette: Aesthetic preferences
            mood_map: Mood patterns
            story_markers: Life events
            device_context: Device configuration
        
        Returns:
            Updated VizzyUserProfile
        """
        profile, _ = VizzyUserProfile.objects.get_or_create(user=user)
        
        if aesthetic_palette is not None:
            profile.aesthetic_palette = aesthetic_palette
        if mood_map is not None:
            profile.mood_map = mood_map
        if story_markers is not None:
            profile.story_markers = story_markers
        if device_context is not None:
            profile.device_context = device_context
        
        profile.save()
        
        # Invalidate cache
        cache_key = f"vizzy:user:{user.id}:profile"
        cache.delete(cache_key)
        
        return profile
    
    @staticmethod
    def invalidate_user_cache(user_id: str) -> None:
        """
        Invalidate all cached data for a user
        
        Args:
            user_id: UUID of user
        """
        patterns = [
            f"vizzy:user:{user_id}:profile",
            f"vizzy:user:{user_id}:recent_moods",
            f"vizzy:user:{user_id}:current_session",
        ]
        
        for pattern in patterns:
            cache.delete(pattern)


class VizzyMoodService:
    """Service for mood tracking and analysis"""
    
    @staticmethod
    @transaction.atomic
    def record_mood(
        user: User,
        valence: float,
        arousal: float,
        emotion_label: str,
        source: str = 'text_analysis',
        session_id: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> VizzyMoodHistory:
        """
        Record a mood data point
        
        Args:
            user: User whose mood is being recorded
            valence: Emotional valence (-1 to 1)
            arousal: Emotional arousal (-1 to 1)
            emotion_label: Emotion label
            source: How mood was determined
            session_id: Optional session UUID
            confidence: Confidence score (0 to 1)
        
        Returns:
            Created VizzyMoodHistory entry
        """
        session = None
        if session_id:
            try:
                session = VizzyChatSession.objects.get(id=session_id)
            except VizzyChatSession.DoesNotExist:
                pass
        
        mood_entry = VizzyMoodHistory.objects.create(
            user=user,
            session=session,
            valence=valence,
            arousal=arousal,
            emotion_label=emotion_label,
            source=source,
            confidence=confidence
        )
        
        # Update user profile mood_map
        VizzyMoodService._update_mood_map(user, valence, arousal, emotion_label)
        
        # Invalidate cache
        cache_key = f"vizzy:user:{user.id}:recent_moods"
        cache.delete(cache_key)
        
        return mood_entry
    
    @staticmethod
    def _update_mood_map(user: User, valence: float, arousal: float, emotion_label: str) -> None:
        """
        Update user's mood_map with latest data
        
        Args:
            user: User to update
            valence: Emotional valence
            arousal: Emotional arousal
            emotion_label: Emotion label
        """
        profile, _ = VizzyUserProfile.objects.get_or_create(user=user)
        
        mood_map = profile.mood_map or {}
        
        # Track emotion frequency
        emotions = mood_map.get('emotions', {})
        emotions[emotion_label] = emotions.get(emotion_label, 0) + 1
        mood_map['emotions'] = emotions
        
        # Track average valence/arousal
        mood_map['avg_valence'] = (
            (mood_map.get('avg_valence', 0) * mood_map.get('total_records', 0) + valence) /
            (mood_map.get('total_records', 0) + 1)
        )
        mood_map['avg_arousal'] = (
            (mood_map.get('avg_arousal', 0) * mood_map.get('total_records', 0) + arousal) /
            (mood_map.get('total_records', 0) + 1)
        )
        mood_map['total_records'] = mood_map.get('total_records', 0) + 1
        mood_map['last_updated'] = timezone.now().isoformat()
        
        profile.mood_map = mood_map
        profile.save(update_fields=['mood_map', 'updated_at'])
    
    @staticmethod
    def get_mood_timeline(user: User, days: int = 30) -> List[Dict]:
        """
        Get mood timeline for user
        
        Args:
            user: User to get timeline for
            days: Number of days to look back
        
        Returns:
            List of mood entries with timestamps
        """
        moods = VizzyMoodHistory.objects.user_mood_timeline(user, days=days)
        
        return [
            {
                'timestamp': mood.timestamp.isoformat(),
                'valence': mood.valence,
                'arousal': mood.arousal,
                'emotion_label': mood.emotion_label,
                'source': mood.source,
                'confidence': mood.confidence,
            }
            for mood in moods
        ]
    
    @staticmethod
    def analyze_mood_patterns(user: User) -> Dict:
        """
        Analyze mood patterns for user
        
        Args:
            user: User to analyze
        
        Returns:
            Dictionary with mood pattern analysis
        """
        from django.db.models import Avg, Count
        from datetime import timedelta
        
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Get mood statistics
        week_stats = VizzyMoodHistory.objects.filter(
            user=user,
            timestamp__gte=week_ago
        ).aggregate(
            avg_valence=Avg('valence'),
            avg_arousal=Avg('arousal'),
            count=Count('id')
        )
        
        month_stats = VizzyMoodHistory.objects.filter(
            user=user,
            timestamp__gte=month_ago
        ).aggregate(
            avg_valence=Avg('valence'),
            avg_arousal=Avg('arousal'),
            count=Count('id')
        )
        
        # Get emotion distribution
        emotion_dist = list(
            VizzyMoodHistory.objects.filter(
                user=user,
                timestamp__gte=week_ago
            ).values('emotion_label').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        )
        
        return {
            'week_summary': {
                'avg_valence': week_stats['avg_valence'],
                'avg_arousal': week_stats['avg_arousal'],
                'entries_count': week_stats['count'],
            },
            'month_summary': {
                'avg_valence': month_stats['avg_valence'],
                'avg_arousal': month_stats['avg_arousal'],
                'entries_count': month_stats['count'],
            },
            'top_emotions': emotion_dist,
        }


class VizzyContextService:
    """Service for managing context data"""
    
    @staticmethod
    @transaction.atomic
    def set_context(
        user: User,
        context_type: str,
        key: str,
        value: any
    ) -> VizzyContextData:
        """
        Set or update context data for user
        
        Args:
            user: User to set context for
            context_type: Type of context
            key: Context key
            value: Context value (JSON-serializable)
        
        Returns:
            Created or updated VizzyContextData
        """
        context, created = VizzyContextData.objects.update_or_create(
            user=user,
            context_type=context_type,
            key=key,
            defaults={'value': value}
        )
        
        # Invalidate user context cache
        VizzyUserContextService.invalidate_user_cache(str(user.id))
        
        return context
    
    @staticmethod
    def get_context(
        user: User,
        context_type: Optional[str] = None,
        key: Optional[str] = None
    ) -> List[VizzyContextData]:
        """
        Get context data for user
        
        Args:
            user: User to get context for
            context_type: Optional type filter
            key: Optional key filter
        
        Returns:
            List of VizzyContextData objects
        """
        qs = VizzyContextData.objects.filter(user=user)
        
        if context_type:
            qs = qs.filter(context_type=context_type)
        if key:
            qs = qs.filter(key=key)
        
        return list(qs.order_by('-access_count'))
    
    @staticmethod
    @transaction.atomic
    def delete_context(user: User, context_id: str) -> bool:
        """
        Delete context data
        
        Args:
            user: User who owns the context
            context_id: UUID of context to delete
        
        Returns:
            True if deleted, False if not found
        """
        try:
            context = VizzyContextData.objects.get(id=context_id, user=user)
            context.delete()
            
            # Invalidate cache
            VizzyUserContextService.invalidate_user_cache(str(user.id))
            
            return True
        except VizzyContextData.DoesNotExist:
            return False
