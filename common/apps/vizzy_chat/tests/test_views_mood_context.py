"""
Comprehensive Tests for Vizzy Mood History and Context Data Views

Tests cover:
- Mood history creation and retrieval
- Mood pattern analysis
- Context data CRUD operations
- Permission checks
"""
import uuid
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.vizzy_chat.models import (
    VizzyChatSession,
    VizzyMoodHistory,
    VizzyContextData,
    VizzyUserProfile
)

User = get_user_model()


class VizzyMoodHistoryViewSetTestCase(APITestCase):
    """Test cases for VizzyMoodHistoryViewSet"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            email='mooduser1@example.com',
            password='testpass123',
            first_name='Mood',
            last_name='User1'
        )
        self.user2 = User.objects.create_user(
            email='mooduser2@example.com',
            password='testpass123'
        )
        
        # Create JWT tokens
        self.user1_token = str(RefreshToken.for_user(self.user1).access_token)
        self.user2_token = str(RefreshToken.for_user(self.user2).access_token)
        
        # Set up API client
        self.client = APIClient()
        
        # Create session for user1
        self.session = VizzyChatSession.objects.create(
            user=self.user1,
            title='Mood Test Session',
            mode='home'
        )
        
        # Create mood history entries
        self.mood1 = VizzyMoodHistory.objects.create(
            user=self.user1,
            session=self.session,
            valence=0.7,
            arousal=0.5,
            emotion_label='happy',
            source='text_analysis',
            confidence=0.85
        )
        self.mood2 = VizzyMoodHistory.objects.create(
            user=self.user1,
            valence=0.3,
            arousal=0.2,
            emotion_label='calm',
            source='explicit_input',
            confidence=1.0
        )
        self.mood3 = VizzyMoodHistory.objects.create(
            user=self.user2,
            valence=-0.5,
            arousal=0.8,
            emotion_label='stressed',
            source='text_analysis',
            confidence=0.75
        )
    
    def test_list_mood_history_authenticated(self):
        """Test listing mood history for authenticated user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # user1 has 2 mood entries
        
        # Verify mood data structure
        mood_data = response.data['results'][0]
        self.assertIn('id', mood_data)
        self.assertIn('valence', mood_data)
        self.assertIn('arousal', mood_data)
        self.assertIn('emotion_label', mood_data)
        self.assertIn('source', mood_data)
        self.assertIn('confidence', mood_data)
        self.assertIn('timestamp', mood_data)
    
    def test_list_mood_history_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('vizzy-chat:mood-history-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_mood_history_only_own_data(self):
        """Test that users only see their own mood data"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only user1's moods are returned
        for mood in response.data['results']:
            self.assertEqual(mood['user']['email'], self.user1.email)
    
    def test_create_mood_history_entry(self):
        """Test creating a new mood history entry"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        data = {
            'valence': 0.6,
            'arousal': 0.4,
            'emotion_label': 'content',
            'source': 'text_analysis',
            'session_id': str(self.session.id),
            'confidence': 0.9
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data['valence']), 0.6)
        self.assertEqual(float(response.data['arousal']), 0.4)
        self.assertEqual(response.data['emotion_label'], 'content')
        
        # Verify entry was created in database
        mood = VizzyMoodHistory.objects.get(id=response.data['id'])
        self.assertEqual(mood.user, self.user1)
    
    def test_create_mood_without_session(self):
        """Test creating mood entry without session"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        data = {
            'valence': -0.3,
            'arousal': 0.7,
            'emotion_label': 'frustrated',
            'source': 'explicit_input'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify session is null
        mood = VizzyMoodHistory.objects.get(id=response.data['id'])
        self.assertIsNone(mood.session)
    
    def test_create_mood_invalid_valence(self):
        """Test creating mood with invalid valence (out of range)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        data = {
            'valence': 1.5,  # Out of range [-1, 1]
            'arousal': 0.5,
            'emotion_label': 'test',
            'source': 'text_analysis'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('valence', response.data)
    
    def test_create_mood_invalid_arousal(self):
        """Test creating mood with invalid arousal (out of range)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        data = {
            'valence': 0.5,
            'arousal': -1.5,  # Out of range [-1, 1]
            'emotion_label': 'test',
            'source': 'text_analysis'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('arousal', response.data)
    
    def test_create_mood_invalid_confidence(self):
        """Test creating mood with invalid confidence (out of range)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        data = {
            'valence': 0.5,
            'arousal': 0.5,
            'emotion_label': 'test',
            'source': 'text_analysis',
            'confidence': 1.5  # Out of range [0, 1]
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confidence', response.data)
    
    def test_analyze_mood_patterns(self):
        """Test mood pattern analysis endpoint"""
        # Create more mood entries for analysis
        now = timezone.now()
        for i in range(10):
            VizzyMoodHistory.objects.create(
                user=self.user1,
                valence=0.5 + (i * 0.05),
                arousal=0.3 + (i * 0.03),
                emotion_label='happy' if i % 2 == 0 else 'calm',
                source='text_analysis',
                timestamp=now - timedelta(days=i)
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-analyze')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('week_summary', response.data)
        self.assertIn('month_summary', response.data)
        self.assertIn('top_emotions', response.data)
        
        # Verify summary structure
        week_summary = response.data['week_summary']
        self.assertIn('avg_valence', week_summary)
        self.assertIn('avg_arousal', week_summary)
        self.assertIn('entries_count', week_summary)
    
    def test_mood_history_pagination(self):
        """Test pagination of mood history list"""
        # Create many mood entries
        for i in range(25):
            VizzyMoodHistory.objects.create(
                user=self.user1,
                valence=0.5,
                arousal=0.3,
                emotion_label='neutral',
                source='text_analysis'
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
    
    def test_user_profile_updated_on_mood_create(self):
        """Test that user profile mood_map is updated when mood is created"""
        # Create or get profile
        profile, _ = VizzyUserProfile.objects.get_or_create(user=self.user1)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:mood-history-list')
        
        data = {
            'valence': 0.8,
            'arousal': 0.6,
            'emotion_label': 'excited',
            'source': 'explicit_input'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify profile mood_map was updated
        profile.refresh_from_db()
        self.assertIsNotNone(profile.mood_map)
        self.assertIn('emotions', profile.mood_map)


class VizzyContextDataViewSetTestCase(APITestCase):
    """Test cases for VizzyContextDataViewSet"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            email='contextdatauser1@example.com',
            password='testpass123',
            first_name='Context',
            last_name='User1'
        )
        self.user2 = User.objects.create_user(
            email='contextdatauser2@example.com',
            password='testpass123'
        )
        
        # Create JWT tokens
        self.user1_token = str(RefreshToken.for_user(self.user1).access_token)
        self.user2_token = str(RefreshToken.for_user(self.user2).access_token)
        
        # Set up API client
        self.client = APIClient()
        
        # Create context data entries
        self.context1 = VizzyContextData.objects.create(
            user=self.user1,
            context_type='preference',
            key='favorite_color',
            value={'primary': 'blue', 'secondary': 'green'}
        )
        self.context2 = VizzyContextData.objects.create(
            user=self.user1,
            context_type='creation',
            key='last_artwork',
            value={'type': 'poster', 'theme': 'nature'}
        )
        self.context3 = VizzyContextData.objects.create(
            user=self.user2,
            context_type='preference',
            key='favorite_artist',
            value={'name': 'Picasso'}
        )
    
    def test_list_context_data_authenticated(self):
        """Test listing context data for authenticated user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # user1 has 2 context entries
        
        # Verify context data structure
        context_data = response.data['results'][0]
        self.assertIn('id', context_data)
        self.assertIn('context_type', context_data)
        self.assertIn('key', context_data)
        self.assertIn('value', context_data)
        self.assertIn('created_at', context_data)
        self.assertIn('access_count', context_data)
    
    def test_list_context_data_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('vizzy-chat:context-data-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_context_data_only_own_data(self):
        """Test that users only see their own context data"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only user1's context data is returned
        for context in response.data['results']:
            self.assertEqual(context['user']['email'], self.user1.email)
    
    def test_filter_context_by_type(self):
        """Test filtering context data by type"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-list')
        
        response = self.client.get(url, {'context_type': 'preference'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['context_type'], 'preference')
    
    def test_create_context_data_entry(self):
        """Test creating a new context data entry"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-list')
        
        data = {
            'context_type': 'knowledge',
            'key': 'art_history',
            'value': {
                'period': 'Renaissance',
                'favorite_works': ['Mona Lisa', 'The Last Supper']
            }
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['context_type'], 'knowledge')
        self.assertEqual(response.data['key'], 'art_history')
        self.assertEqual(response.data['value']['period'], 'Renaissance')
        
        # Verify entry was created in database
        context = VizzyContextData.objects.get(id=response.data['id'])
        self.assertEqual(context.user, self.user1)
    
    def test_create_context_invalid_type(self):
        """Test creating context with invalid type"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-list')
        
        data = {
            'context_type': 'invalid_type',
            'key': 'test',
            'value': {'test': 'data'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('context_type', response.data)
    
    def test_create_duplicate_context_key(self):
        """Test creating duplicate context (same user, type, key)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-list')
        
        # Try to create context with same key as context1
        data = {
            'context_type': 'preference',
            'key': 'favorite_color',
            'value': {'primary': 'red'}
        }
        
        response = self.client.post(url, data, format='json')
        
        # Should either update existing or reject with 400
        # Depending on implementation (update_or_create vs create)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_retrieve_context_data_detail(self):
        """Test retrieving specific context data"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-detail', kwargs={'pk': self.context1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.context1.id))
        self.assertEqual(response.data['key'], 'favorite_color')
    
    def test_retrieve_context_data_not_owned(self):
        """Test that users cannot retrieve context data they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-detail', kwargs={'pk': self.context3.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_context_data(self):
        """Test deleting context data"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-detail', kwargs={'pk': self.context1.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify entry was deleted
        self.assertFalse(VizzyContextData.objects.filter(id=self.context1.id).exists())
    
    def test_delete_context_data_not_owned(self):
        """Test that users cannot delete context data they don't own"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-detail', kwargs={'pk': self.context3.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify entry still exists
        self.assertTrue(VizzyContextData.objects.filter(id=self.context3.id).exists())
    
    def test_context_data_access_count_increment(self):
        """Test that access_count is incremented on retrieval"""
        initial_count = self.context1.access_count
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-detail', kwargs={'pk': self.context1.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify access_count was incremented
        self.context1.refresh_from_db()
        self.assertEqual(self.context1.access_count, initial_count + 1)
    
    def test_context_data_pagination(self):
        """Test pagination of context data list"""
        # Create many context entries
        for i in range(25):
            VizzyContextData.objects.create(
                user=self.user1,
                context_type='preference',
                key=f'test_key_{i}',
                value={'data': f'value_{i}'}
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user1_token}')
        url = reverse('vizzy-chat:context-data-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
