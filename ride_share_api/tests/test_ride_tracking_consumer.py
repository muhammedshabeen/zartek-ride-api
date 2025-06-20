from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from core.asgi import application
from django.contrib.auth import get_user_model
from ride_share_api.models import Ride
from asgiref.sync import sync_to_async

User = get_user_model()

class RideTrackingConsumerTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.rider = User.objects.create_user(username='rider1', password='pass', role='1')
        self.driver = User.objects.create_user(username='driver1', password='pass', role='2')
        self.ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_location='Start',
            dropoff_location='End',
            status='STARTED'
        )
        self.path = f"/ws/track/{self.ride.id}/"

    async def test_send_location_and_update_ride(self):
        communicator = WebsocketCommunicator(application, self.path)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({
            'latitude': 12.9716,
            'longitude': 77.5946,
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response['latitude'], 12.9716)
        self.assertEqual(response['longitude'], 77.5946)

        await self._refresh_ride()
        self.assertEqual(float(self.ride.latitude), 12.9716)
        self.assertEqual(float(self.ride.longitude), 77.5946)

        await communicator.disconnect()

    @sync_to_async
    def _refresh_ride(self):
        self.ride.refresh_from_db()
