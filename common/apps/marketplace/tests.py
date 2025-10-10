from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Price

class PriceAPITestCase(APITestCase):
	def setUp(self):
		self.price = Price.objects.create(
			image='example.jpg',
			price=19.99,
			size='M',
			canvas_ratio='4:3',
			active=True,
		)
		self.list_url = reverse('price-list')  # uses router basename

	def test_list_prices(self):
		response = self.client.get(self.list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response.data), 1)

	def test_create_price(self):
		data = {
			'image': 'new.jpg',
			'price': 29.99,
			'size': 'L',
			'canvas_ratio': '16:9',
			'active': True,
		}
		response = self.client.post(self.list_url, data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Price.objects.count(), 2)
from django.test import TestCase

# Create your tests here.
