from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps  # Importamos apps en lugar de los modelos directamente

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Cargar mensajes existentes
        conversation = await self.get_conversation()
        if conversation:
            await self.send(text_data=json.dumps({
                'messages': conversation.messages
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        sender_username = data['sender']

        sender = await self.get_user(sender_username)
        if sender:
            await self.save_message(sender, message_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': sender_username,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))

    @sync_to_async
    def get_user(self, username):
        User = apps.get_model('auth', 'User')  # Importamos User aquí
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    async def save_message(self, sender, content):
        Conversation = apps.get_model('users', 'Conversation')  # Importamos Conversation aquí

        # Esperar el resultado de get_conversation
        conversation = await self.get_conversation()
        if conversation:
            # Concatenar el nuevo mensaje al campo `messages`
            new_message = f"{sender.username}: {content}\n"
            conversation.messages += new_message
            await sync_to_async(conversation.save)()  # Guardar la conversación actualizada

    @sync_to_async
    def get_conversation(self):
        Conversation = apps.get_model('users', 'Conversation')  # Importamos Conversation aquí
        try:
            return Conversation.objects.get(id=self.conversation_id)
        except Conversation.DoesNotExist:
            return None