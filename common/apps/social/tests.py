from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Post, Follow
from apps.gallery.models import Image
import uuid

User = get_user_model()

class UserProfileAPITestCase(APITestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(username='user1', email='u1@example.com', password='pass')
        self.user2 = User.objects.create_user(username='user2', email='u2@example.com', password='pass')
        # Create a post for user2
        self.post = Post.objects.create(user=self.user2)
        # Create images and attach to post (if Image model exists)
        # Skip image creation if gallery app not fully set up
        try:
            img = Image.objects.create(uploaded_by=self.user2)
            self.post.images.add(img)
        except Exception:
            pass

    def test_public_profile_visible(self):
        url = reverse('user-profile', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('posts', response.data)

    def test_private_profile_blocked(self):
        # Set profile to private
        self.user2.profile_visible = False
        self.user2.save()
        url = reverse('user-profile', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_follow_status(self):
        # user1 follows user2
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.client.login(username='user1', password='pass')
        url = reverse('user-profile', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('is_following'))
