from django.contrib.auth.models import AbstractUser
from django.db import models
from core.utils import BaseModel

ROLE_CHOICES = (
    ('1', 'Rider'),
    ('2', 'Driver'),
)

status_choices = (
    ('REQUESTED','Requested'),
    ('STARTED','Started'),
    ('COMPLETED','Completed'),
    ('CANCELLED','Cancelled'),
)

class CustomUser(AbstractUser):
    name = models.CharField(max_length=255,)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='RIDER')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
   
class Ride(BaseModel):
    rider = models.ForeignKey(CustomUser, related_name='rider_details', on_delete=models.CASCADE,null=True, blank=True)
    driver = models.ForeignKey(CustomUser, related_name='driver_details',on_delete=models.SET_NULL, null=True, blank=True)
    pickup_location = models.CharField(max_length=100)
    dropoff_location = models.CharField(max_length=100)
    status = models.CharField(max_length=20,default="REQUESTED",choices=status_choices)
    driver_accepted = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    

    def __str__(self):
        return str(self.id)
    
