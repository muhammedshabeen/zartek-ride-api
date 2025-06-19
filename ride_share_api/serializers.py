from rest_framework import serializers
from .models import *

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'name', 'phone_number', 'role','latitude','longitude')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if not attrs.get('name'):
            raise serializers.ValidationError({"name": "Name is required."})

        if not attrs.get('phone_number'):
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        
        if CustomUser.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "Email is already exist"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'name', 'email',
            'phone_number', 'role', 'role_display',
            'latitude', 'longitude'
        ]
        read_only_fields = ['id', 'username', 'role']

    def get_role_display(self, obj):
        return obj.get_role_display()

class RideSerializer(serializers.ModelSerializer):
    rider = UserSerializer(read_only=True)
    driver = UserSerializer(read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id', 'rider', 'driver',
            'pickup_location', 'dropoff_location',
            'status', 'driver_accepted',
            'latitude', 'longitude',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'rider', 'driver', 'status', 'driver_accepted', 'created_at', 'updated_at']