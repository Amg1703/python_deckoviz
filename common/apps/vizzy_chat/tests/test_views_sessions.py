"""
Comprehensive Tests for Vizzy Chat Session Views

Tests cover:
- Authentication and permissions
- CRUD operations
- Query optimization
- Error handling
- Edge cases
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


class VizzyChatSessionViewSetTestCase(APITestCase):
    """Test cases for VizzyChatSessionViewSet"""
    
    def setUp(self):
        """Set up test data and authenticated client"""
        # Create test users
        self.user1 = User.objects.create_user(
            email='testuser1@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User1'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@example.com',
            password='testpass123',
            first_name='Test',
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
            title='Test Session 1',
            mode='home'
        )
        self.session2 = VizzyChatSession.objects.create(
            user=self.user1,
            title='Test Session 2',
            mode='enterprise',
            is_active=False
        )
        self.session3 = VizzyChatSession.objects.create(
            user=self.user2,
            title='User 2 Session',
            mode='home'
        )
        
        # Create some messages
        VizzyChatMessage.objects.create(
            session=self.session1,
            role='user',
            content='Hello Vizzy!'
        )
        VizzyChatMessage.objects.create(
            session=self.session1,
            role='assistant',
            content='Hello! How can I help you today?'
        )
    
    def test_list_sessions_authenticated(self):
        """Test listing sessions for authenticated user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        # Include inactive sessions to see all 2 sessions
        response = self.client.get(url, {'active_only': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # user1 has 2 sessions
        
        # Verify session data structure
        session_data = response.data['results'][0]
        self.assertIn('id', session_data)
        self.assertIn('user', session_data)
        self.assertIn('title', session_data)
        self.assertIn('mode', session_data)
        self.assertIn('is_active', session_data)
        self.assertIn('message_count', session_data)
        self.assertIn('created_at', session_data)
    
    def test_list_sessions_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('vizzy-chat:session-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_sessions_active_only_filter(self):
        """Test filtering to only active sessions"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        response = self.client.get(url, {'active_only': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only 1 active session
        self.assertTrue(response.data['results'][0]['is_active'])
    
    def test_list_sessions_include_inactive(self):
        """Test including inactive sessions"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        response = self.client.get(url, {'active_only': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Both active and inactive
    
    def test_retrieve_session_detail(self):
        """Test retrieving a specific session with messages"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': self.session1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.session1.id))
        self.assertEqual(response.data['title'], 'Test Session 1')
        self.assertIn('messages', response.data)
        self.assertEqual(len(response.data['messages']), 2)  # 2 messages created
    
    def test_retrieve_session_not_owned(self):
        """Test that users cannot retrieve sessions they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': self.session3.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_session_not_found(self):
        """Test retrieving non-existent session"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        fake_id = uuid.uuid4()
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': fake_id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_session_home_mode(self):
        """Test creating a new session in home mode"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        data = {
            'mode': 'home',
            'title': 'New Test Session'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Test Session')
        self.assertEqual(response.data['mode'], 'home')
        self.assertTrue(response.data['is_active'])
        self.assertEqual(response.data['message_count'], 0)
        
        # Verify session was created in database
        session = VizzyChatSession.objects.get(id=response.data['id'])
        self.assertEqual(session.user, self.user1)
    
    def test_create_session_enterprise_mode(self):
        """Test creating a session in enterprise mode"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        data = {
            'mode': 'enterprise',
            'title': 'Enterprise Session'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['mode'], 'enterprise')
    
    def test_create_session_without_title(self):
        """Test creating a session without title (should succeed)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        data = {
            'mode': 'home'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['title'])
    
    def test_create_session_invalid_mode(self):
        """Test creating a session with invalid mode"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        data = {
            'mode': 'invalid_mode'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('mode', response.data)
    
    def test_update_session_title(self):
        """Test updating session title"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': self.session1.id})
        
        data = {
            'title': 'Updated Title'
        }
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        
        # Verify in database
        self.session1.refresh_from_db()
        self.assertEqual(self.session1.title, 'Updated Title')
    
    def test_update_session_mode(self):
        """Test updating session mode"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': self.session1.id})
        
        data = {
            'mode': 'enterprise'
        }
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mode'], 'enterprise')
    
    def test_update_session_not_owned(self):
        """Test that users cannot update sessions they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': self.session3.id})
        
        data = {
            'title': 'Hacked Title'
        }
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify session was not updated
        self.session3.refresh_from_db()
        self.assertNotEqual(self.session3.title, 'Hacked Title')
    
    def test_close_session_action(self):
        """Test closing an active session"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-close', kwargs={'pk': self.session1.id})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify session is closed
        self.session1.refresh_from_db()
        self.assertFalse(self.session1.is_active)
        self.assertIsNotNone(self.session1.closed_at)
    
    def test_close_already_closed_session(self):
        """Test closing an already closed session"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-close', kwargs={'pk': self.session2.id})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('already closed', response.data['message'].lower())
    
    def test_close_session_not_owned(self):
        """Test that users cannot close sessions they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-close', kwargs={'pk': self.session3.id})
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_session(self):
        """Test deleting a session"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': self.session1.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify session is soft deleted (still exists but is_active=False)
        self.assertTrue(VizzyChatSession.objects.filter(id=self.session1.id).exists())
        self.session1.refresh_from_db()
        self.assertFalse(self.session1.is_active)
    
    def test_delete_session_not_owned(self):
        """Test that users cannot delete sessions they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-detail', kwargs={'pk': self.session3.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify session still exists
        self.assertTrue(VizzyChatSession.objects.filter(id=self.session3.id).exists())
    
    def test_session_list_pagination(self):
        """Test pagination of session list"""
        # Create many sessions
        for i in range(25):
            VizzyChatSession.objects.create(
                user=self.user1,
                title=f'Session {i}',
                mode='home'
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
    
    def test_session_list_custom_page_size(self):
        """Test custom page size"""
        # Create more sessions
        for i in range(15):
            VizzyChatSession.objects.create(
                user=self.user1,
                title=f'Session {i}',
                mode='home'
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        response = self.client.get(url, {'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
    
    def test_user_profile_created_on_session_create(self):
        """Test that user profile is created/updated when session is created"""
        # Ensure no profile exists
        VizzyUserProfile.objects.filter(user=self.user1).delete()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:session-list')
        
        data = {'mode': 'home', 'title': 'Profile Test Session'}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify profile was created
        profile = VizzyUserProfile.objects.get(user=self.user1)
        self.assertIsNotNone(profile)
        self.assertGreater(profile.total_sessions, 0)
