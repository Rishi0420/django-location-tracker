import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Get user_id from URL (e.g. ws://.../?user_id=2)
        query_string = self.scope['query_string'].decode()
        params = dict(q.split('=')
                      for q in query_string.split('&') if '=' in q)
        track_user_id = params.get('user_id')

        target_user_id = self.user.id
        # If the admin is tracking another user
        if self.user.is_staff and track_user_id:
            target_user_id = track_user_id

        self.room_group_name = f'user_{target_user_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leaving the group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # If a message arrives from WebSocket (we are not currently using this function)
    async def receive(self, text_data):
        pass

    # To send a message to a client when it arrives from a group
    async def location_update(self, event):
        location_data = event['location']
        await self.send(text_data=json.dumps(location_data))

    # geofence.alert handler
    async def geofence_alert(self, event):
        alert_message = event['alert']
        await self.send(text_data=json.dumps({
            'type': 'geofence_alert',
            'message': alert_message
        }))

    # New handler: To send a command from the admin to the client
    async def send_command(self, event):
        command = event['command']

        # Sending commands in JSON format to a client via WebSocket
        await self.send(text_data=json.dumps({
            'type': 'command',
            'command': command,
        }))
