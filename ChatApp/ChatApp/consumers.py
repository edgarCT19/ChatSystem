import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f"group_{self.room_name}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify group members that a user has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.scope['user'].username,
                'timestamp': str(timezone.now()),  # Current timestamp
                'local_time': str(timezone.localtime()),  # Current local time
                'message_type': 'join'  # Message type for join event
            }
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify group members that a user has left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.scope['user'].username,
                'timestamp': str(timezone.now()),  # Current timestamp
                'local_time': str(timezone.localtime()),  # Current local time
                'message_type': 'leave'  # Message type for leave event
            }
        )

    async def receive(self, text_data):
        # Handle incoming messages
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        timestamp = text_data_json.get("timestamp", "")
        local_time = text_data_json.get("local_time", "")
        
        # Send the received message to all group members
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_message',
                'message': message,
                'username': username,
                'timestamp': timestamp,
                'local_time': local_time
            }
        )

    async def user_joined(self, event):
        now = datetime.datetime.now()
        formatted_local_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        message = f'{event["username"]} se ha unido al chat. ({formatted_local_time})'
        await self.send_notification(message, event)

    async def user_left(self, event):
        now = datetime.datetime.now()
        formatted_local_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        message = f'{event["username"]} se ha salido del chat. ({formatted_local_time})'
        await self.send_notification(message, event)

    async def send_notification(self, message, event):
        username = 'System'  # Use 'System' as the sender of system notifications
        timestamp = event['timestamp']
        local_time = event['local_time']
        message_type = event['message_type']  # Get the message type
        
        # Send notification message to WebSocket with message type
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
            'local_time': local_time,
            'type': message_type  # Include the message type in the message data
        }))

    async def send_message(self, event):
        message = event["message"]
        username = event["username"]
        timestamp = event["timestamp"]
        local_time = event["local_time"]
        
        # Send regular chat message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp,
            'local_time': local_time
        }))
