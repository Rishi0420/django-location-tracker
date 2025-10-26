from rest_framework import serializers
from .models import Location, Geofence
from django.contrib.auth.models import User


class LocationSerializer(serializers.ModelSerializer):
    # Use FloatField for Latitude and Longitude so that float values ​​in JSON are accepted.
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = Location
        fields = ['id', 'user', 'latitude',
                  'longitude', 'timestamp', 'battery_level']
        read_only_fields = ['id', 'user', 'timestamp']


class GeofenceSerializer(serializers.ModelSerializer):
    # To display only the username of user_to_track
    user_to_track_username = serializers.ReadOnlyField(
        source='user_to_track.username')

    class Meta:
        model = Geofence
        fields = [
            'id',
            'name',
            'user_to_track',
            'user_to_track_username',
            'latitude',
            'longitude',
            'radius'
        ]
        read_only_fields = ['created_by']  # this will set automatically
