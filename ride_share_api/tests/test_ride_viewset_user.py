from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth import get_user_model
from ride_share_api.models import Ride

User = get_user_model()

class RideViewSetUserTest(APITestCase):
    def setUp(self):
        self.rider = User.objects.create_user(username='rider', password='pass', role='1')
        self.driver = User.objects.create_user(username='driver', password='pass', role='2')

        Ride.objects.create(rider=self.rider, driver=self.driver, pickup_location='A', dropoff_location='B', status='COMPLETED')
        Ride.objects.create(rider=self.rider, pickup_location='C', dropoff_location='D', status='REQUESTED')

        self.token_rider = Token.objects.create(user=self.rider)
        self.token_driver = Token.objects.create(user=self.driver)

        self.url = reverse('ride-get-user-rides')

    def test_rider_ride_list_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_rider.key)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['count'], 2)

    def test_driver_ride_list_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_driver.key)
        response = self.client.get(self.url)  
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['count'], 1)

    def test_no_rides_returned(self):
        new_user = User.objects.create_user(username='empty_user', password='pass', role='1')
        token = Token.objects.create(user=new_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(self.url)  
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['status'])
        self.assertEqual(response.data['count'], 0)
