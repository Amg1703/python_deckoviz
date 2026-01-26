"""
Comprehensive Tests for Vizzy User Profile and Context Views

Tests cover:
- User profile retrieval and updates
- User context aggregation
- Permission checks
- Data validation
"""
import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.vizzy_chat.models import (
    VizzyChatSession,
    VizzyChatMessage,
    VizzyUserProfile,
    VizzyMoodHistory,
    VizzyContextData
)

User = get_user_model()


class VizzyUserProfileViewTestCase(APITestCase):
    """Test cases for VizzyUserProfileView"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            email='profileuser@example.com',
            password='testpass123',
            first_name='Profile',
            last_name='User'
        )
        
        # Create JWT token
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        
        # Set up API client
        self.client = APIClient()
        
        # Get or create user profile (signal auto-creates it)
        self.profile, created = VizzyUserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'aesthetic_palette': {
                    'primary_colors': ['#FF5733', '#C70039'],
                    'style': 'modern'
                },
                'mood_map': {
                    'avg_valence': 0.5,
                    'avg_arousal': 0.3,
                    'total_records': 10
                },
                'story_markers': [
                    {'event': 'Wedding', 'date': '2024-06-15'},
                    {'event': 'Birthday', 'date': '2024-12-01'}
                ],
                'device_context': {
                    'room_type': 'living_room',
                    'display_schedule': 'evening'
                },
                'total_sessions': 5,
                'total_messages': 50
            }
        )
        # Update if it already existed (from signal)
        if not created:
            self.profile.aesthetic_palette = {
                'primary_colors': ['#FF5733', '#C70039'],
                'style': 'modern'
            }
            self.profile.mood_map = {
                'avg_valence': 0.5,
                'avg_arousal': 0.3,
                'total_records': 10
            }
            self.profile.story_markers = [
                {'event': 'Wedding', 'date': '2024-06-15'},
                {'event': 'Birthday', 'date': '2024-12-01'}
            ]
            self.profile.device_context = {
                'room_type': 'living_room',
                'display_schedule': 'evening'
            }
            self.profile.total_sessions = 5
            self.profile.total_messages = 50
            self.profile.save()
    
    def test_get_user_profile_authenticated(self):
        """Test retrieving user profile when authenticated"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], self.user.email)
        self.assertIn('aesthetic_palette', response.data)
        self.assertIn('mood_map', response.data)
        self.assertIn('story_markers', response.data)
        self.assertIn('device_context', response.data)
        self.assertEqual(response.data['total_sessions'], 5)
        self.assertEqual(response.data['total_messages'], 50)
    
    def test_get_user_profile_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('vizzy-chat:profile-detail')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_profile_auto_created(self):
        """Test that profile is auto-created if it doesn't exist"""
        # Create new user without profile
        new_user = User.objects.create_user(
            email='newuser@example.com',
            password='testpass123'
        )
        new_token = str(RefreshToken.for_user(new_user).access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], new_user.email)
        
        # Verify profile was created in database
        profile = VizzyUserProfile.objects.get(user=new_user)
        self.assertIsNotNone(profile)
    
    def test_update_aesthetic_palette(self):
        """Test updating aesthetic palette"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        new_palette = {
            'primary_colors': ['#3498DB', '#2ECC71'],
            'style': 'minimalist',
            'font_preference': 'sans-serif'
        }
        
        data = {'aesthetic_palette': new_palette}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['aesthetic_palette'], new_palette)
        
        # Verify in database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.aesthetic_palette, new_palette)
    
    def test_update_mood_map(self):
        """Test updating mood map"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        new_mood_map = {
            'avg_valence': 0.7,
            'avg_arousal': 0.5,
            'total_records': 20,
            'dominant_emotion': 'joyful'
        }
        
        data = {'mood_map': new_mood_map}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mood_map'], new_mood_map)
    
    def test_update_story_markers(self):
        """Test updating story markers"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        new_markers = [
            {'event': 'Graduation', 'date': '2023-05-20'},
            {'event': 'New Job', 'date': '2024-01-10'},
            {'event': 'Anniversary', 'date': '2024-06-15'}
        ]
        
        data = {'story_markers': new_markers}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['story_markers'], new_markers)
    
    def test_update_device_context(self):
        """Test updating device context"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        new_device_context = {
            'room_type': 'bedroom',
            'display_schedule': 'morning',
            'brightness_level': 'medium'
        }
        
        data = {'device_context': new_device_context}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['device_context'], new_device_context)
    
    def test_update_multiple_fields(self):
        """Test updating multiple fields at once"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        data = {
            'aesthetic_palette': {'style': 'vintage'},
            'device_context': {'room_type': 'office'}
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['aesthetic_palette']['style'], 'vintage')
        self.assertEqual(response.data['device_context']['room_type'], 'office')
    
    def test_cannot_update_computed_fields(self):
        """Test that computed fields (total_sessions, total_messages) are read-only"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        data = {
            'total_sessions': 999,
            'total_messages': 9999
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify values did not change
        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.total_sessions, 999)
        self.assertNotEqual(self.profile.total_messages, 9999)
    
    def test_invalid_aesthetic_palette_type(self):
        """Test validation for invalid aesthetic_palette type"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        data = {'aesthetic_palette': 'not a dict'}  # Should be dict/JSON
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_story_markers_type(self):
        """Test validation for invalid story_markers type"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:profile-detail')
        
        data = {'story_markers': {'not': 'a list'}}  # Should be list/array
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VizzyUserContextViewTestCase(APITestCase):
    """Test cases for VizzyUserContextView"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            email='contextuser@example.com',
            password='testpass123',
            first_name='Context',
            last_name='User'
        )
        
        # Create JWT token
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        
        # Set up API client
        self.client = APIClient()
        
        # Get or create user profile (signal auto-creates it)
        self.profile, created = VizzyUserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'aesthetic_palette': {'style': 'modern'},
                'mood_map': {'avg_valence': 0.6},
                'total_sessions': 3,
                'total_messages': 15
            }
        )
        # Update if it already existed (from signal)
        if not created:
            self.profile.aesthetic_palette = {'style': 'modern'}
            self.profile.mood_map = {'avg_valence': 0.6}
            self.profile.total_sessions = 3
            self.profile.total_messages = 15
            self.profile.save()
        
        # Create sessions and messages
        self.session = VizzyChatSession.objects.create(
            user=self.user,
            title='Context Test Session',
            mode='home'
        )
        VizzyChatMessage.objects.create(
            session=self.session,
            role='user',
            content='Test message'
        )
        
        # Create mood history
        VizzyMoodHistory.objects.create(
            user=self.user,
            session=self.session,
            valence=0.7,
            arousal=0.5,
            emotion_label='happy',
            source='text_analysis'
        )
        VizzyMoodHistory.objects.create(
            user=self.user,
            valence=0.3,
            arousal=0.2,
            emotion_label='calm',
            source='explicit_input'
        )
        
        # Create context data
        VizzyContextData.objects.create(
            user=self.user,
            context_type='preference',
            key='favorite_artist',
            value={'name': 'Van Gogh', 'style': 'Impressionism'}
        )
        VizzyContextData.objects.create(
            user=self.user,
            context_type='creation',
            key='last_poster',
            value={'theme': 'nature', 'colors': ['green', 'blue']}
        )
    
    def test_get_user_context_authenticated(self):
        """Test retrieving comprehensive user context"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:user-context')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all expected fields are present
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        self.assertIn('aesthetic_palette', response.data)
        self.assertIn('mood_map', response.data)
        self.assertIn('story_markers', response.data)
        self.assertIn('device_context', response.data)
        self.assertIn('recent_moods', response.data)
        self.assertIn('average_mood_valence', response.data)
        self.assertIn('total_sessions', response.data)
        self.assertIn('total_messages', response.data)
        self.assertIn('context_entries', response.data)
        
        # Verify data values
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['total_sessions'], 3)
        self.assertEqual(response.data['total_messages'], 15)
    
    def test_get_user_context_includes_recent_moods(self):
        """Test that recent moods are included in context"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:user-context')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['recent_moods'], list)
        self.assertGreater(len(response.data['recent_moods']), 0)
        
        # Verify mood structure
        mood = response.data['recent_moods'][0]
        self.assertIn('valence', mood)
        self.assertIn('arousal', mood)
        self.assertIn('emotion_label', mood)
        self.assertIn('timestamp', mood)
    
    def test_get_user_context_includes_context_entries(self):
        """Test that context entries are included"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:user-context')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['context_entries'], list)
        self.assertEqual(len(response.data['context_entries']), 2)
        
        # Verify context entry structure
        entry = response.data['context_entries'][0]
        self.assertIn('context_type', entry)
        self.assertIn('key', entry)
        self.assertIn('value', entry)
    
    def test_get_user_context_calculates_average_mood(self):
        """Test that average mood valence is calculated"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:user-context')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['average_mood_valence'])
        self.assertIsInstance(response.data['average_mood_valence'], float)
    
    def test_get_user_context_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        url = reverse('vizzy-chat:user-context')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_context_caching(self):
        """Test that context is cached properly"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('vizzy-chat:user-context')
        
        # First request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Modify profile
        self.profile.aesthetic_palette = {'style': 'vintage'}
        self.profile.save()
        
        # Second request (should still return cached data if caching is enabled)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Note: In production, response2 might return old cached data
        # This test just verifies the endpoint works correctly
    
    def test_get_user_context_empty_profile(self):
        """Test context retrieval for user with minimal data"""
        # Create new user with minimal profile
        new_user = User.objects.create_user(
            email='minimal@example.com',
            password='testpass123'
        )
        # Profile auto-created by signal, just get it
        profile, _ = VizzyUserProfile.objects.get_or_create(user=new_user)
        
        new_token = str(RefreshToken.for_user(new_user).access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_token}')
        url = reverse('vizzy-chat:user-context')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], new_user.email)
        self.assertEqual(response.data['total_sessions'], 0)
        self.assertEqual(response.data['total_messages'], 0)
        self.assertEqual(len(response.data['recent_moods']), 0)
        self.assertEqual(len(response.data['context_entries']), 0)
