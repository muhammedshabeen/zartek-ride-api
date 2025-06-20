from rest_framework.test import APITestCase
from django.urls import reverse
from ride_share_api.models import Ride, CustomUser
from rest_framework.authtoken.models import Token

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
