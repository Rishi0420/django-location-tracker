from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, permissions
from .models import Location
from .serializers import LocationSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required   # only for login users
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from .forms import UserRegisterForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from datetime import datetime
from rest_framework import permissions, status
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from .models import Geofence
from .serializers import GeofenceSerializer

# To convert a date string to an object
from django.utils.dateparse import parse_date

# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class LocationListCreateView(generics.ListCreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Location.objects.all()

        # User filtering for admins
        user_id = self.request.query_params.get('user_id', None)
        if user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=user)

        # New: Filtering by date
        date_filter_str = self.request.query_params.get('date', None)
        if date_filter_str:
            # Convert the string 'YYYY-MM-DD' to a date object
            target_date = parse_date(date_filter_str)
            if target_date:
                # Filter data for only the selected date
                queryset = queryset.filter(timestamp__date=target_date)

        # Sort in order from oldest to newest.
        return queryset.order_by('timestamp')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LatestLocationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        last_timestamp_str = request.query_params.get('since', None)
        user_id = request.query_params.get('user_id', None)

        # Decide whose location you want to get.
        target_user = self.request.user
        if self.request.user.is_staff and user_id:
            try:
                target_user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        queryset = Location.objects.filter(user=target_user)

        if last_timestamp_str:
            try:
                last_timestamp = datetime.fromisoformat(
                    last_timestamp_str.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gt=last_timestamp)
            except (ValueError, TypeError):
                pass

        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)


# New Class: UserListView
@method_decorator(csrf_exempt, name='dispatch')
class UserListView(APIView):
    """
    हा व्ह्यू फक्त स्टाफ/ॲडमिन युजर्सना सर्व युजर्सची यादी देतो.
    """
    permission_classes = [
        permissions.IsAdminUser]  # Only admin can access

    def get(self, request):
        users = User.objects.all().values('id', 'username')  # Just send the id and username
        return Response(users)


# New View: GeofenceListCreateView
@method_decorator(csrf_exempt, name='dispatch')
class GeofenceListCreateView(generics.ListCreateAPIView):
    serializer_class = GeofenceSerializer
    permission_classes = [permissions.IsAdminUser]  # only admin can user this

    def get_queryset(self):
        # Get all geofences created by the admin
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Geofence.objects.filter(created_by=self.request.user, user_to_track_id=user_id)
        return Geofence.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        # Set the current admin user as created_by when creating a geofence.
        serializer.save(created_by=self.request.user)


# New View: GeofenceRetrieveUpdateDestroyView
@method_decorator(csrf_exempt, name='dispatch')
class GeofenceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GeofenceSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        # Admin can only delete/update geofences created by him/her
        return Geofence.objects.filter(created_by=self.request.user)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class SendCommandView(APIView):
    permission_classes = [permissions.IsAdminUser]  # only admin can use this

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        command = request.data.get('command')

        if not user_id or not command:
            return Response({'error': 'user_id and command are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Send a message to the WebSocket group
        channel_layer = get_channel_layer()
        user_group_name = f'user_{user.id}'

        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                # A new handler will be needed in the Consumer
                'type': 'send_command',
                'command': command
            }
        )

        return Response({'status': f'Command "{command}" sent to user {user.username}.'})


@login_required  # This view can only be accessed by logged-in users.
def map_view(request):
    # Here you don't need to pass any data, as the map will take the data via the API in JavaScript.
    return render(request, 'tracker_app/map.html')


@login_required
def track_device_view(request):
    """
    This page will be used to send location when opened in a mobile browser.
    """
    return render(request, 'tracker_app/track.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user
            return redirect('map_view')  # Redirect to map page
    else:
        form = UserRegisterForm()
    return render(request, 'tracker_app/register.html', {'form': form})


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)  # only for admin users
def admin_dashboard_view(request):
    return render(request, 'tracker_app/dashboard.html')


def home_view(request):
    return render(request, 'tracker_app/home.html')
