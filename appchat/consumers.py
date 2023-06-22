from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# from .models import ChatMessage, ChatRoom

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('New client connect! ')
        # Подключение клиента
        await self.accept()

        # Получение параметров запроса, в данном случае slug комнаты
        self.room_slug = 'chat' # self.scope['url_route']['kwargs']['room_slug']

        # Присоединение к группе чата, используя slug комнаты
        await self.channel_layer.group_add(
            self.room_slug,
            self.channel_name
        )

    async def disconnect(self, close_code):
        # Отключение клиента
        await self.channel_layer.group_discard(
            self.room_slug,
            self.channel_name
        )

    async def receive(self, text_data):
        print(text_data)
        # Получение сообщения от клиента
        await self.send_message(text_data)

    async def send_message(self, text_data):
        # Отправка сообщения клиенту и сохранение в базе данных
        # sender = self.scope['user']
        # message = await self.create_message(sender, text_data)

        # Отправка сообщения всем клиентам в группе чата
        await self.channel_layer.group_send(
            self.room_slug,
            {
                'type': 'chat_message',
                'sender': 'I',
                'message': 'HI-HI-HI'
            }
        )

    async def chat_message(self, event):
        # Получение сообщения из группы чата и отправка его клиенту
        await self.send(text_data=event['message'])

    # @database_sync_to_async
    # def create_message(self, sender, message):
    #     # Создание и сохранение сообщения в базе данных
    #     # chat_room = ChatRoom.objects.get(slug=self.room_slug)
    #     # new_message = ChatMessage.objects.create(chat_room=chat_room, sender=sender, message=message)
    #     return new_message
