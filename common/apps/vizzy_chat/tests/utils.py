"""
Test Utilities and Fixtures for Vizzy Chat Tests

Provides reusable test utilities, fixtures, and helper functions
"""
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from apps.vizzy_chat.models import (
    VizzyChatSession,
    VizzyChatMessage,
    VizzyUserProfile,
    VizzyMoodHistory,
    VizzyContextData
)

User = get_user_model()


class VizzyChatTestMixin:
    """
    Mixin class providing common test utilities for Vizzy Chat tests
    
    Usage:
        class MyTestCase(VizzyChatTestMixin, APITestCase):
            def setUp(self):
                self.setup_test_user()
                self.setup_test_session()
    """
    
    def setup_test_user(self, email='test@example.com', password='testpass123'):
        """Create a test user and JWT token"""
        self.user = User.objects.create_user(
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        return self.user, self.user_token
    
    def setup_test_session(self, user=None, title='Test Session', mode='home'):
        """Create a test session"""
        if user is None:
            user = self.user
        
        self.session = VizzyChatSession.objects.create(
            user=user,
            title=title,
            mode=mode
        )
        return self.session
    
    def setup_test_messages(self, session=None, count=5):
        """Create test messages in a session"""
        if session is None:
            session = self.session
        
        messages = []
        for i in range(count):
            role = 'user' if i % 2 == 0 else 'assistant'
            message = VizzyChatMessage.objects.create(
                session=session,
                role=role,
                content=f'Test message {i+1}'
            )
            messages.append(message)
        
        return messages
    
    def setup_test_profile(self, user=None):
        """Create a test user profile"""
        if user is None:
            user = self.user
        
        self.profile = VizzyUserProfile.objects.create(
            user=user,
            aesthetic_palette={'style': 'modern'},
            mood_map={'avg_valence': 0.5},
            total_sessions=0,
            total_messages=0
        )
        return self.profile
    
    def setup_test_mood_history(self, user=None, count=5):
        """Create test mood history entries"""
        if user is None:
            user = self.user
        
        moods = []
        for i in range(count):
            mood = VizzyMoodHistory.objects.create(
                user=user,
                valence=0.5,
                arousal=0.3,
                emotion_label='neutral',
                source='text_analysis'
            )
            moods.append(mood)
        
        return moods
    
    def setup_test_context_data(self, user=None, count=3):
        """Create test context data entries"""
        if user is None:
            user = self.user
        
        contexts = []
        for i in range(count):
            context = VizzyContextData.objects.create(
                user=user,
                context_type='preference',
                key=f'test_key_{i}',
                value={'data': f'value_{i}'}
            )
            contexts.append(context)
        
        return contexts
    
    def authenticate_client(self, token=None):
        """Authenticate the test client"""
        if token is None:
            token = self.user_token
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def clear_authentication(self):
        """Clear authentication from test client"""
        self.client.credentials()


def create_test_user(email='test@example.com', password='testpass123', **kwargs):
    """
    Helper function to create a test user
    
    Args:
        email: User email
        password: User password
        **kwargs: Additional user fields
    
    Returns:
        User instance
    """
    return User.objects.create_user(
        email=email,
        password=password,
        **kwargs
    )


def create_test_session(user, title='Test Session', mode='home', **kwargs):
    """
    Helper function to create a test session
    
    Args:
        user: Session owner
        title: Session title
        mode: Session mode
        **kwargs: Additional session fields
    
    Returns:
        VizzyChatSession instance
    """
    return VizzyChatSession.objects.create(
        user=user,
        title=title,
        mode=mode,
        **kwargs
    )


def create_test_message(session, role='user', content='Test message', **kwargs):
    """
    Helper function to create a test message
    
    Args:
        session: Parent session
        role: Message role
        content: Message content
        **kwargs: Additional message fields
    
    Returns:
        VizzyChatMessage instance
    """
    return VizzyChatMessage.objects.create(
        session=session,
        role=role,
        content=content,
        **kwargs
    )


def get_jwt_token(user):
    """
    Get JWT access token for user
    
    Args:
        user: User instance
    
    Returns:
        JWT access token string
    """
    return str(RefreshToken.for_user(user).access_token)


class TestDataFactory:
    """
    Factory class for creating test data
    
    Usage:
        factory = TestDataFactory()
        user = factory.create_user()
        session = factory.create_session(user)
        messages = factory.create_messages(session, count=10)
    """
    
    @staticmethod
    def create_user(email=None, password='testpass123', **kwargs):
        """Create a test user"""
        if email is None:
            import uuid
            email = f'test_{uuid.uuid4().hex[:8]}@example.com'
        
        return User.objects.create_user(
            email=email,
            password=password,
            first_name=kwargs.get('first_name', 'Test'),
            last_name=kwargs.get('last_name', 'User'),
            **{k: v for k, v in kwargs.items() if k not in ['first_name', 'last_name']}
        )
    
    @staticmethod
    def create_session(user, **kwargs):
        """Create a test session"""
        defaults = {
            'title': 'Test Session',
            'mode': 'home'
        }
        defaults.update(kwargs)
        return VizzyChatSession.objects.create(user=user, **defaults)
    
    @staticmethod
    def create_messages(session, count=5, **kwargs):
        """Create multiple test messages"""
        messages = []
        for i in range(count):
            role = kwargs.get('role', 'user' if i % 2 == 0 else 'assistant')
            content = kwargs.get('content', f'Test message {i+1}')
            
            message = VizzyChatMessage.objects.create(
                session=session,
                role=role,
                content=content
            )
            messages.append(message)
        
        return messages
    
    @staticmethod
    def create_profile(user, **kwargs):
        """Create a test user profile"""
        defaults = {
            'aesthetic_palette': {'style': 'modern'},
            'mood_map': {'avg_valence': 0.5},
            'story_markers': [],
            'device_context': {}
        }
        defaults.update(kwargs)
        return VizzyUserProfile.objects.create(user=user, **defaults)
    
    @staticmethod
    def create_mood_history(user, session=None, **kwargs):
        """Create a test mood history entry"""
        defaults = {
            'valence': 0.5,
            'arousal': 0.3,
            'emotion_label': 'neutral',
            'source': 'text_analysis'
        }
        defaults.update(kwargs)
        return VizzyMoodHistory.objects.create(
            user=user,
            session=session,
            **defaults
        )
    
    @staticmethod
    def create_context_data(user, **kwargs):
        """Create a test context data entry"""
        defaults = {
            'context_type': 'preference',
            'key': 'test_key',
            'value': {'data': 'test_value'}
        }
        defaults.update(kwargs)
        return VizzyContextData.objects.create(user=user, **defaults)
