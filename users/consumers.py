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

        # Carregar els missatges de la conversa
        conversation = await self.get_conversation()
        if conversation:
            messages = conversation.messages.split('\n')
            formatted_messages = []
            for msg in messages:
                if msg.strip(): #Es un .trim() a python el .strip()
                    sender, content = msg.split(': ', 1) # Divideix el missatge en dues parts: l'usuari i el contingut
                    formatted_messages.append({'sender': sender, 'content': content.strip()}) # Afegeix el missatge formatat conversa

            await self.send(text_data=json.dumps({
                'messages': formatted_messages # Enviem els missatges formatats al client
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, # Només es fa servir per a la desconexió
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message'] 
        sender_username = data['sender'] 

        sender = await self.get_user(sender_username)
        if sender:
            await self.save_message(sender, message_content) # Guardar el missatge a la base de dades

        await self.channel_layer.group_send(
            self.room_group_name, # Enviem el missatge al grup de la conversa
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
        User = apps.get_model('auth', 'User')  
        try:
            return User.objects.get(username=username) # Obtenim a l'usuari
        except User.DoesNotExist:
            return None # Si no existeix, retornem None

    async def save_message(self, sender, content):
        Conversation = apps.get_model('users', 'Conversation')

        
        conversation = await self.get_conversation()
        if conversation:
            
            new_message = f"{sender.username}: {content}\n"
            conversation.messages += new_message # Afegim el nou missatge a la conversa
            await sync_to_async(conversation.save)()  # Actualitzem la conversa amb el nou missatge

    @sync_to_async
    def get_conversation(self):
        Conversation = apps.get_model('users', 'Conversation') 
        try:
            return Conversation.objects.get(id=self.conversation_id) # Obtenim la conversa per ID
        except Conversation.DoesNotExist:
            return None