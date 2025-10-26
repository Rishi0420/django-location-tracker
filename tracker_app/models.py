from django.db import models
from django.contrib.auth.models import User

# Imports required for signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from geopy.distance import geodesic


# Create your models here.

class Location(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(
        auto_now_add=True)  # time when Location is recorded

    battery_level = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']  # new location can be seen first

    def __str__(self):
        return f"Location of {self.user.username} at {self.timestamp}"


class Geofence(models.Model):
    name = models.CharField(max_length=100)
    # Which user is the geofence for (who wants to monitor)
    user_to_track = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='geofences')
    # Who created the geofence (admin)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_geofences')
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6)  # Center of the circle (Lat)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6)  # Center of the circle (Lng)
    radius = models.FloatField()  # Radius in meter
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Geofence '{self.name}' for {self.user_to_track.username}"


class GeofenceStatus(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='geofence_status')
    last_known_geofence = models.ForeignKey(
        Geofence, null=True, blank=True, on_delete=models.SET_NULL)
    is_inside = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Inside" if self.is_inside else "Outside"
        fence_name = self.last_known_geofence.name if self.last_known_geofence else "N/A"
        return f"{self.user.username} is {status} '{fence_name}'"


# This function will run when the new Location object is saved
@receiver(post_save, sender=Location)
def check_geofence_and_notify(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user
    current_location = (instance.latitude, instance.longitude)

    # 1. First send location updates via WebSocket (this is the same as before)
    channel_layer = get_channel_layer()
    user_group_name = f'user_{user.id}'
    location_data = {
        'latitude': str(instance.latitude),
        'longitude': str(instance.longitude),
        'timestamp': instance.timestamp.isoformat(),
        'battery_level': instance.battery_level,
    }
    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {'type': 'location.update', 'location': location_data}
    )

    # 2. Geofence inspection logic
    user_geofences = Geofence.objects.filter(user_to_track=user)
    user_status, _ = GeofenceStatus.objects.get_or_create(user=user)

    was_inside = user_status.is_inside
    currently_inside = False
    current_geofence = None

    for fence in user_geofences:
        fence_center = (fence.latitude, fence.longitude)
        distance = geodesic(current_location, fence_center).meters

        if distance <= fence.radius:
            currently_inside = True
            current_geofence = fence
            break  # Stop the loop when detected in a geofence

    # Check if the state has changed.
    if was_inside != currently_inside:
        # update state
        user_status.is_inside = currently_inside
        user_status.last_known_geofence = current_geofence
        user_status.save()

        # Determine the type of event
        event_type = "ENTER" if currently_inside else "EXIT"
        message = f"User '{user.username}' has {event_type}ED the geofence '{current_geofence.name if current_geofence else user_status.last_known_geofence.name}'."

        # Send notifications to admin via WebSocket
        admin_user = current_geofence.created_by if current_geofence else user_status.last_known_geofence.created_by
        if admin_user:  # <--- Add this check
            admin_group_name = f'user_{admin_user.id}'

        # For debugging
        print(f"Sending geofence alert to {admin_group_name}: {message}")

        async_to_sync(channel_layer.group_send)(
            admin_group_name,
            {
                # A new handler will be required in the Consumer
                'type': 'geofence.alert',
                'alert': message
            }
        )
