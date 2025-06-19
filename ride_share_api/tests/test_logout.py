# ride_share_api/tests/test_logout.py

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class LogoutApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='logoutuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.logout_url = reverse('logout')

    def test_successful_logout(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], True)
        self.assertEqual(response.data['message'], 'Logged out successfully.')

        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=self.user)

    def test_logout_without_token(self):
        self.client.credentials()  
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 401)  
