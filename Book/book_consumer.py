
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the user ID from the URL or query parameters
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"notifications_{self.user_id}"

        # Add the user to their notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print("connected")

    async def disconnect(self, close_code):
        # Remove the user from their notification group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        # Send the notification message to the WebSocket
        message = event['message']
        print("message",message)
        await self.send(text_data=json.dumps({
            'message': message
        }))