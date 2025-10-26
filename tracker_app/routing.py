from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/location_updates/$', consumers.LocationConsumer.as_asgi()),
]
