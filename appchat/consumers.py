from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncJsonWebsocketConsumer):

    @database_sync_to_async
    def get_room(self, user):
        return user.chat_rooms.all().get(slug=self.room_slug)

    async def connect(self):
        user = self.scope.get('user')
        if user and user.is_authenticated:
            print('Connect :', user.username)
            # Пользователь аутентифицирован, разрешить подключение
            await self.accept()

            # Получение параметров запроса, в данном случае slug комнаты
            self.room_slug = self.scope['url_route']['kwargs']['room_slug']
            room = await self.get_room(user)
            print('Connect to room:', room)
            # Присоединение к группе чата, используя slug комнаты
            await self.channel_layer.group_add(
                self.room_slug,
                self.channel_name
            )

        else:
            # Пользователь не аутентифицирован, закрыть соединение
            await self.close()

    async def disconnect(self, close_code):
        # Отключение клиента
        await self.channel_layer.group_discard(
            self.room_slug,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        message = content.get('message')
        sender = content.get('sender')

        # Отправка сообщения в группу чата
        await self.channel_layer.group_send(
            self.room_slug,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )

    async def chat_message(self, event):
        message = event.get('message')
        sender = event.get('sender')

        # Отправка сообщения клиенту
        await self.send_json({
            'type': 'chat_message',
            'sender': sender,
            'message': message
        })
