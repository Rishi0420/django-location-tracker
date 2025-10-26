import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        query_string = self.scope['query_string'].decode()
        params = dict(q.split('=')
                      for q in query_string.split('&') if '=' in q)
        track_user_id = params.get('user_id')

        target_user_id = self.user.id
        if self.user.is_staff and track_user_id:
            target_user_id = track_user_id

        self.room_group_name = f'user_{target_user_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Handles location updates sent from the backend (signals)
    async def location_update(self, event):
        location_data = event['location']
        await self.send(text_data=json.dumps(location_data))

    # Handles geofence alerts sent from the backend
    async def geofence_alert(self, event):
        alert_message = event['alert']
        await self.send(text_data=json.dumps({
            'type': 'geofence_alert',
            'message': alert_message
        }))

    # Handles commands sent from the admin
    async def send_command(self, event):
        command = event['command']
        await self.send(text_data=json.dumps({
            'type': 'command',
            'command': command,
        }))
