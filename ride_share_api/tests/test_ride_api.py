from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ride_share_api.models import Ride
from rest_framework.authtoken.models import Token

User = get_user_model()

class RideViewSetTest(APITestCase):
    def setUp(self):
        self.rider = User.objects.create_user(
            username='rider1',
            email='rider1@example.com',
            password='testpass',
            role='1',  # Rider
            latitude=12.9716,
            longitude=77.5946
        )
        self.driver = User.objects.create_user(
            username='driver1',
            email='driver1@example.com',
            password='testpass',
            role='2',  # Driver
            latitude=12.9611,
            longitude=77.6387
        )

        self.token = Token.objects.create(user=self.rider)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.ride_create_url = reverse('ride-list')  # Default ModelViewSet route

    def test_create_ride_and_assign_driver(self):
        data = {
            'pickup_location': 'Location A',
            'dropoff_location': 'Location B',
            'latitude': 12.9716,
            'longitude': 77.5946,
        }
        response = self.client.post(self.ride_create_url, data)
        self.assertEqual(response.status_code, 201)
        ride = Ride.objects.get(id=response.data['id'])
        self.assertIsNotNone(ride.driver)
        self.assertEqual(ride.status, 'REQUESTED')

    def test_create_ride_without_location_no_driver(self):
        data = {
            'pickup_location': 'No Loc A',
            'dropoff_location': 'No Loc B'
        }
        response = self.client.post(self.ride_create_url, data)
        self.assertEqual(response.status_code, 201)
        ride = Ride.objects.get(id=response.data['id'])
        self.assertIsNone(ride.driver)

    def test_update_ride_status_success(self):
        # First create ride
        data = {
            'pickup_location': 'A',
            'dropoff_location': 'B',
            'latitude': 12.9716,
            'longitude': 77.5946,
        }
        response = self.client.post(self.ride_create_url, data)
        ride_id = response.data['id']
        ride = Ride.objects.get(id=ride_id)

        # Login as the assigned driver
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get_or_create(user=ride.driver)[0].key)
        update_url = reverse('ride-update-status', args=[ride_id])
        update_response = self.client.post(update_url, {'status': 'STARTED'})

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data['ride']['status'], 'STARTED')

    def test_update_ride_status_invalid_status(self):
        data = {
            'pickup_location': 'A',
            'dropoff_location': 'B',
            'latitude': 12.9716,
            'longitude': 77.5946,
        }
        response = self.client.post(self.ride_create_url, data)
        ride = Ride.objects.get(id=response.data['id'])

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get_or_create(user=ride.driver)[0].key)
        update_url = reverse('ride-update-status', args=[ride.id])
        update_response = self.client.post(update_url, {'status': 'FLYING'})  # Invalid

        self.assertEqual(update_response.status_code, 400)
        self.assertIn('Invalid status', update_response.data['error'])

    def test_update_ride_status_unauthorized_user(self):
        data = {
            'pickup_location': 'A',
            'dropoff_location': 'B',
            'latitude': 12.9716,
            'longitude': 77.5946,
        }
        response = self.client.post(self.ride_create_url, data)
        ride = Ride.objects.get(id=response.data['id'])

        # Login as someone who is not the assigned driver
        other_user = User.objects.create_user(username='fake', password='123', role='2')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get_or_create(user=other_user)[0].key)

        update_url = reverse('ride-update-status', args=[ride.id])
        update_response = self.client.post(update_url, {'status': 'STARTED'})

        self.assertEqual(update_response.status_code, 403)
        self.assertIn('Not authorized', update_response.data['error'])
