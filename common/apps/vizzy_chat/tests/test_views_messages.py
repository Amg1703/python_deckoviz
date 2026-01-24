"""
Comprehensive Tests for Vizzy Chat Message Views

Tests cover:
- Message CRUD operations
- Session ownership validation
- Multimodal message support
- Emotional context tracking
- Performance metrics
"""
import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.vizzy_chat.models import VizzyChatSession, VizzyChatMessage, VizzyUserProfile

User = get_user_model()


class VizzyChatMessageViewSetTestCase(APITestCase):
    """Test cases for VizzyChatMessageViewSet"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            email='messageuser1@example.com',
            password='testpass123',
            first_name='Message',
            last_name='User1'
        )
        self.user2 = User.objects.create_user(
            email='messageuser2@example.com',
            password='testpass123',
            first_name='Message',
            last_name='User2'
        )
        
        # Create JWT tokens
        self.user1_token = str(RefreshToken.for_user(self.user1).access_token)
        self.user2_token = str(RefreshToken.for_user(self.user2).access_token)
        
        # Set up API client
        self.client = APIClient()
        
        # Create test sessions
        self.session1 = VizzyChatSession.objects.create(
            user=self.user1,
            title='Message Test Session',
            mode='home'
        )
        self.session2 = VizzyChatSession.objects.create(
            user=self.user2,
            title='User 2 Session',
            mode='home'
        )
        
        # Create test messages
        self.message1 = VizzyChatMessage.objects.create(
            session=self.session1,
            role='user',
            content='Hello Vizzy, how are you?'
        )
        self.message2 = VizzyChatMessage.objects.create(
            session=self.session1,
            role='assistant',
            content="I'm doing great! How can I assist you today?",
            detected_emotion='joyful',
            mood_valence=0.8,
            mood_arousal=0.6
        )
        self.message3 = VizzyChatMessage.objects.create(
            session=self.session2,
            role='user',
            content='This is user 2 message'
        )
    
    def test_list_messages_in_session(self):
        """Test listing all messages in a session"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verify message structure
        message_data = response.data['results'][0]
        self.assertIn('id', message_data)
        self.assertIn('role', message_data)
        self.assertIn('content', message_data)
        self.assertIn('created_at', message_data)
    
    def test_list_messages_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_messages_wrong_user(self):
        """Test that users cannot list messages from sessions they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session2.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_message_detail(self):
        """Test retrieving a specific message"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-detail', kwargs={
            'session_pk': self.session1.id,
            'pk': self.message1.id
        })
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.message1.id))
        self.assertEqual(response.data['content'], 'Hello Vizzy, how are you?')
        self.assertEqual(response.data['role'], 'user')
    
    def test_retrieve_message_wrong_session(self):
        """Test retrieving a message from wrong session"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        # Try to access message3 (belongs to session2) through session1 URL
        url = reverse('vizzy-chat:session-message-detail', kwargs={
            'session_pk': self.session1.id,
            'pk': self.message3.id
        })
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_user_message(self):
        """Test creating a user message"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'user',
            'content': 'Can you help me create a poster?'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'user')
        self.assertEqual(response.data['content'], 'Can you help me create a poster?')
        self.assertFalse(response.data['has_images'])
        
        # Verify message was created in database
        message = VizzyChatMessage.objects.get(id=response.data['id'])
        self.assertEqual(message.session, self.session1)
        
        # Verify session message count was updated
        self.session1.refresh_from_db()
        self.assertEqual(self.session1.message_count, 3)  # 2 existing + 1 new
    
    def test_create_assistant_message(self):
        """Test creating an assistant message"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'assistant',
            'content': "Of course! I'd be happy to help you create a poster.",
            'detected_emotion': 'helpful',
            'mood_valence': 0.7,
            'mood_arousal': 0.5,
            'tokens_used': 150,
            'processing_time_ms': 1250
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'assistant')
        self.assertEqual(response.data['detected_emotion'], 'helpful')
        self.assertEqual(float(response.data['mood_valence']), 0.7)
        self.assertEqual(float(response.data['mood_arousal']), 0.5)
        self.assertEqual(response.data['tokens_used'], 150)
        self.assertEqual(response.data['processing_time_ms'], 1250)
    
    def test_create_message_with_images(self):
        """Test creating a message with images"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'user',
            'content': 'Check out these images',
            'has_images': True,
            'image_urls': [
                'https://s3.amazonaws.com/deckoviz/image1.jpg',
                'https://s3.amazonaws.com/deckoviz/image2.jpg'
            ]
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['has_images'])
        self.assertEqual(len(response.data['image_urls']), 2)
    
    def test_create_message_invalid_role(self):
        """Test creating a message with invalid role"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'invalid_role',
            'content': 'Test message'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)
    
    def test_create_message_invalid_mood_valence(self):
        """Test creating a message with out-of-range mood valence"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'assistant',
            'content': 'Test message',
            'mood_valence': 1.5  # Out of range [-1, 1]
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('mood_valence', response.data)
    
    def test_create_message_invalid_mood_arousal(self):
        """Test creating a message with out-of-range mood arousal"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'assistant',
            'content': 'Test message',
            'mood_arousal': -2.0  # Out of range [-1, 1]
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('mood_arousal', response.data)
    
    def test_create_message_has_images_without_urls(self):
        """Test validation: has_images=True but no image_urls provided"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'user',
            'content': 'Test message',
            'has_images': True,
            'image_urls': []
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_message_wrong_session(self):
        """Test that users cannot create messages in sessions they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session2.id})
        
        data = {
            'role': 'user',
            'content': 'Hacking attempt'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify no message was created
        self.assertFalse(
            VizzyChatMessage.objects.filter(
                session=self.session2,
                content='Hacking attempt'
            ).exists()
        )
    
    def test_message_list_pagination(self):
        """Test pagination of message list"""
        # Create many messages
        for i in range(25):
            VizzyChatMessage.objects.create(
                session=self.session1,
                role='user' if i % 2 == 0 else 'assistant',
                content=f'Message {i}'
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
    
    def test_message_ordering(self):
        """Test that messages are ordered by creation time"""
        # Create messages with specific order
        msg1 = VizzyChatMessage.objects.create(
            session=self.session1,
            role='user',
            content='First message'
        )
        msg2 = VizzyChatMessage.objects.create(
            session=self.session1,
            role='assistant',
            content='Second message'
        )
        msg3 = VizzyChatMessage.objects.create(
            session=self.session1,
            role='user',
            content='Third message'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # First message should be the oldest (message1 from setUp)
        messages = response.data['results']
        self.assertEqual(messages[0]['content'], 'Hello Vizzy, how are you?')
        
        # Last message should be the newest
        self.assertEqual(messages[-1]['content'], 'Third message')
    
    def test_user_profile_updated_on_message_create(self):
        """Test that user profile message count is updated when user sends message"""
        # Get or create profile
        profile, _ = VizzyUserProfile.objects.get_or_create(user=self.user1)
        initial_message_count = profile.total_messages
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        data = {
            'role': 'user',
            'content': 'Test message for profile update'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify profile was updated
        profile.refresh_from_db()
        self.assertEqual(profile.total_messages, initial_message_count + 1)
    
    def test_session_updated_on_message_create(self):
        """Test that session's last_message_at and message_count are updated"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-list', kwargs={'session_pk': self.session1.id})
        
        initial_count = self.session1.message_count
        
        data = {
            'role': 'user',
            'content': 'Test session update'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify session was updated
        self.session1.refresh_from_db()
        self.assertIsNotNone(self.session1.last_message_at)
        self.assertEqual(self.session1.message_count, initial_count + 1)
    
    def test_cannot_update_message(self):
        """Test that messages cannot be updated (immutable)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-detail', kwargs={
            'session_pk': self.session1.id,
            'pk': self.message1.id
        })
        
        data = {
            'content': 'Modified content'
        }
        
        response = self.client.patch(url, data)
        
        # Should return 405 Method Not Allowed if update is not allowed
        # or 200 but content should not change
        self.message1.refresh_from_db()
        self.assertNotEqual(self.message1.content, 'Modified content')
    
    def test_cannot_delete_message(self):
        """Test that messages cannot be deleted (for audit trail)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-message-detail', kwargs={
            'session_pk': self.session1.id,
            'pk': self.message1.id
        })
        
        response = self.client.delete(url)
        
        # Should return 405 Method Not Allowed
        # Verify message still exists
        self.assertTrue(VizzyChatMessage.objects.filter(id=self.message1.id).exists())
