from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth import get_user_model
from ride_share_api.models import Ride

User = get_user_model()

class RideAcceptanceTest(APITestCase):
    def setUp(self):
        self.driver = User.objects.create_user(
            username='driver1', password='testpass', role='2'
        )
        self.rider = User.objects.create_user(
            username='rider1', password='testpass', role='1'
        )
        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_location='A',
            dropoff_location='B',
            status='REQUESTED'
        )
        self.accept_url = reverse('ride-accept-ride', kwargs={'pk': self.ride.id})

    def test_accept_ride_success(self):
        token = Token.objects.get_or_create(user=self.driver)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.accept_url, {'ride_id': self.ride.id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['status'])
        self.assertIn('You have accepted the ride', response.data['message'])

    def test_accept_ride_not_found(self):
        token = Token.objects.get_or_create(user=self.driver)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        invalid_url = reverse('ride-accept-ride', kwargs={'pk': 9999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_accept_ride_already_accepted(self):
        self.ride.driver_accepted = True
        self.ride.save()
        token = Token.objects.get_or_create(user=self.driver)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.accept_url, {'ride_id': self.ride.id})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Ride already accepted', response.data['message'])

    def test_accept_ride_by_unauthorized_user(self):
        other_driver = User.objects.create_user(username='driver2', password='testpass', role='2')
        token = Token.objects.get_or_create(user=other_driver)[0]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.accept_url, {'ride_id': self.ride.id})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.data['status'])
