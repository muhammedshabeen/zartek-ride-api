

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from core.utils import haversine
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action

#Local Imports
from .models import *
from .serializers import *


class LoginApiView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                user_serializer = UserRegistrationSerializer(user)
                latitude = request.data.get('latitude', None)  
                longitude = request.data.get('longitude', None)
                if latitude and longitude:
                    user.latitude = latitude
                    user.longitude = longitude
                    user.save() 
                return Response({
                    "status": True,
                    "message": 'Logged in successfully.',
                    "token": token.key,
                    "user_details": user_serializer.data,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'status': False, 'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({
                "status": True,
                "message": "Logged out successfully."
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "status": False,
                "message": "Something went wrong during logout."
            }, status=status.HTTP_400_BAD_REQUEST)




class RegistrationApiView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'status': True,
                'message': 'User created successfully',
                "token": token.key,
                "user_details": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                    "phone_number": user.phone_number,
                    "role": user.get_role_display(),
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": False,
                "messages": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)



# class RideViewSet(viewsets.ModelViewSet):
#     queryset = Ride.objects.all()
#     serializer_class = RideSerializer
#     permission_classes = [IsAuthenticated]

#     @action(detail=True, methods=['post'], url_path='match-driver')
#     def match_driver(self, request, pk=None):
#         ride = self.get_object()

#         if ride.driver or ride.status != 'REQUESTED':
#             return Response({'message': 'Ride already matched or not in requested state'}, status=400)

#         rider_lat = ride.latitude
#         rider_lng = ride.longitude

#         if not rider_lat or not rider_lng:
#             return Response({'error': 'Ride location missing'}, status=400)

#         # Filter available drivers (with location)
#         drivers = CustomUser.objects.filter(role='2', latitude__isnull=False, longitude__isnull=False)

#         if not drivers:
#             return Response({'error': 'No available drivers'}, status=404)

#         distances = []
#         for driver in drivers:
#             url = (
#                 f"https://maps.googleapis.com/maps/api/distancematrix/json?"
#                 f"origins={driver.latitude},{driver.longitude}&"
#                 f"destinations={rider_lat},{rider_lng}&"
#                 f"key={settings.GOOGLE_MAPS_API_KEY}"
#             )
#             response = requests.get(url).json()
#             try:
#                 distance_value = response['rows'][0]['elements'][0]['distance']['value']  # in meters
#                 distances.append((driver, distance_value))
#             except (KeyError, IndexError):
#                 continue

#         if not distances:
#             return Response({'error': 'Distance calculation failed'}, status=500)

#         # Sort by closest
#         closest_driver = sorted(distances, key=lambda x: x[1])[0][0]
#         ride.driver = closest_driver
#         ride.status = 'STARTED'
#         ride.driver_accepted = True
#         ride.save()

#         return Response({
#             'message': f'Driver {closest_driver.name} assigned.',
#             'ride': RideSerializer(ride).data
#         })



class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ride = serializer.save(rider=self.request.user)

        rider_lat = ride.latitude
        rider_lng = ride.longitude

        if not rider_lat or not rider_lng:
            return  

        drivers = CustomUser.objects.filter(role='2',latitude__isnull=False,longitude__isnull=False)
        print("DRIVER",drivers)

        if not drivers:
            return  

        distances = []
        for driver in drivers:
            try:
                distance_km = haversine(
                    float(driver.latitude),
                    float(driver.longitude),
                    float(rider_lat),
                    float(rider_lng)
                )
                distances.append((driver, distance_km))
            except Exception:
                continue
        print("distances",distances)
        if not distances:
            return  

        closest_driver = sorted(distances, key=lambda x: x[1])[0][0]
        ride.driver = closest_driver
        ride.status = 'REQUESTED'
        ride.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    @action(detail=True, methods=['post'], url_path='accept')
    def accept_ride(self, request, pk=None):
        ride = self.get_object()

        if ride.status != 'REQUESTED':
            return Response({'status': False, 'message': 'Ride is not in requested state'}, status=status.HTTP_400_BAD_REQUEST)

        if ride.driver_accepted:
            return Response({'status': False, 'message': 'Ride already accepted'}, status=status.HTTP_400_BAD_REQUEST)

        if ride.driver != request.user:
            return Response({'status': False, 'message': 'You are not authorized to accept this ride'}, status=status.HTTP_403_FORBIDDEN)

        # Accept the ride
        ride.status = 'STARTED'
        ride.driver_accepted = True
        ride.save()

        rider_name = ride.rider.get_full_name() if ride.rider else 'Unknown'

        return Response({
            'status': True,
            'message': f"You have accepted the ride {ride.id}.\n"
                       f"Rider: {rider_name}\n"
                       f"Pickup: {ride.pickup_location}\n"
                       f"Dropoff: {ride.dropoff_location}",
            'ride': RideSerializer(ride).data
        }, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['post'], url_path='match-driver')
    def match_driver(self, request, pk=None):
        ride = self.get_object()
        user = request.user

        if user.role != '2':
            return Response({
                'status': False,
                'message': 'Only drivers can be assigned to rides.'
            }, status=status.HTTP_403_FORBIDDEN)

        if ride.driver:
            return Response({
                'status': False,
                'message': 'Ride already has a driver.'
            }, status=status.HTTP_400_BAD_REQUEST)


        ride.driver = user
        ride.status = 'REQUESTED'
        ride.save()

        return Response({
            'status': True,
            'message': f'Driver {user.username} has been assigned to ride {ride.id}.',
            'ride': RideSerializer(ride).data
        }, status=status.HTTP_200_OK)




    
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        ride = self.get_object()
        user = request.user
        new_status = request.data.get('status')

        valid_statuses = ['STARTED', 'COMPLETED', 'CANCELLED']

        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        if ride.driver != user:
            return Response({'error': 'Not authorized to update this ride'}, status=status.HTTP_403_FORBIDDEN)

        ride.status = new_status
        ride.save()

        return Response({
            'message': f'Ride status updated to {new_status}',
            'ride': RideSerializer(ride).data
        }, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['get'], url_path='my-rides')
    def get_user_rides(self, request):
        user = request.user
        if not user:
            return Response({
                'status': False,
                'message': "Authentication Failed"
            }, status=status.HTTP_400_BAD_REQUEST)
        queryset = Ride.objects.all()
        if user.role == '1':
            queryset = queryset.filter(rider=user)
        elif user.role == '2':
            queryset = queryset.filter(driver=user)
        else:
            return Response({
                'status': False,
                'message': "User role mismatch"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': True,
            'count': queryset.count(),
            'rides': serializer.data
        })

    