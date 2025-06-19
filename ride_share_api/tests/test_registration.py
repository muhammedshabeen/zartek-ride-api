# ride_share_api/tests/test_registration.py

from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationApiTest(APITestCase):
    def setUp(self):
        self.registration_url = reverse('register')

    def test_successful_registration(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'pass1234',
            'password2': 'pass1234',
            'name': 'Test User',
            'phone_number': '1234567890',
            'role': 1,
            'latitude': 12.9716,
            'longitude': 77.5946
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['status'])
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user_details']['email'], data['email'])

    def test_password_mismatch(self):
        data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'pass1234',
            'password2': 'wrongpass',
            'name': 'Test User',
            'phone_number': '1234567890',
            'role': 2
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['status'])
        self.assertIn('password', response.data['messages'])

    def test_missing_required_fields(self):
        response = self.client.post(self.registration_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['status'])
        self.assertIn('email', response.data['messages'])
        self.assertIn('name', response.data['messages'])
        self.assertIn('phone_number', response.data['messages'])

    def test_duplicate_email(self):
        User.objects.create_user(username='existing', email='duplicate@example.com', password='pass')
        data = {
            'username': 'testuser3',
            'email': 'duplicate@example.com',
            'password': 'pass1234',
            'password2': 'pass1234',
            'name': 'Test User',
            'phone_number': '9876543210',
            'role': 1
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['status'])
        self.assertIn('email', response.data['messages'])
