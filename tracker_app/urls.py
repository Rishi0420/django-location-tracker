from django.urls import path
from .views import LocationListCreateView, CustomAuthToken, LatestLocationsView, UserListView, SendCommandView, GeofenceListCreateView, GeofenceRetrieveUpdateDestroyView

app_name = 'tracker_app'

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),

    path('geofences/', GeofenceListCreateView.as_view(),
         name='geofence-list-create'),

    path('geofences/<int:pk>/',
         GeofenceRetrieveUpdateDestroyView.as_view(), name='geofence-detail'),

    path('locations/', LocationListCreateView.as_view(),
         name='location-list-create'),

    path('latest-locations/', LatestLocationsView.as_view(),
         name='latest-locations'),

    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),

    path('send-command/', SendCommandView.as_view(), name='send-command'),
]
