from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/track/<int:ride_id>/', consumers.RideTrackingConsumer.as_asgi()),
]