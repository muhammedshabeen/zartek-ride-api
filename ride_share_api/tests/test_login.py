from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.urls import reverse

User = get_user_model()

class LoginApiViewTest(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_success_without_location(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['status'], True)

    def test_login_success_with_location(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'latitude': 12.9716,
            'longitude': 77.5946
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(float(self.user.latitude), 12.9716)
        self.assertEqual(float(self.user.longitude), 77.5946)

    def test_login_failure_wrong_password(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], False)
        self.assertEqual(response.data['message'], 'Invalid credentials.')

    def test_login_failure_missing_fields(self):
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
        self.assertIn('password', response.data)
