from rest_framework.test import APITestCase
from django.urls import reverse
from ride_share_api.models import Ride, CustomUser
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
User = get_user_model()

class RideMatchingTest(APITestCase):
    def setUp(self):
        self.rider = CustomUser.objects.create_user(username='rider1', password='pass', role='1', latitude=12.9716, longitude=77.5946)
        self.driver1 = CustomUser.objects.create_user(username='driver1', password='pass', role='2', latitude=12.9718, longitude=77.5947)
        self.driver2 = CustomUser.objects.create_user(username='driver2', password='pass', role='2', latitude=12.9000, longitude=77.5000)
        self.token = Token.objects.create(user=self.rider)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_nearest_driver_assigned(self):
        data = {
            "pickup_location": "Start",
            "dropoff_location": "End",
            "latitude": 12.9716,
            "longitude": 77.5946
        }
        response = self.client.post(reverse('ride-list'), data)
        self.assertEqual(response.status_code, 201)
        ride = Ride.objects.get(id=response.data['id'])
        self.assertEqual(ride.driver.username, 'driver1')


class RideTrackingTest(APITestCase):
    def setUp(self):
        self.driver = User.objects.create_user(username='driver', password='pass', role='2')
        self.rider = User.objects.create_user(username='rider', password='pass', role='1')
        self.ride = Ride.objects.create(rider=self.rider, driver=self.driver, status='STARTED')
        self.token = Token.objects.create(user=self.driver)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_update_driver_location(self):
        self.driver.latitude = '11.0'
        self.driver.longitude = '76.0'
        self.driver.save()
        self.driver.refresh_from_db()
        self.assertAlmostEqual(float(self.driver.latitude), 11.0)
        self.assertAlmostEqual(float(self.driver.longitude), 76.0)

