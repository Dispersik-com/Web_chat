from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncJsonWebsocketConsumer):

    @database_sync_to_async
    def get_room(self, user):
        return user.chat_rooms.all().get(slug=self.room_slug)

    @database_sync_to_async
    def add_message(self, sender, message):
        message = self.room.add_message(sender, message)
        if message is None:
            return False
        return True

    async def connect(self):
        user = self.scope.get('user')
        if user and user.is_authenticated:
            # print('Connect:', user.username)
            # Користувач автентифікований, дозволити підключення
            await self.accept()

            # Отримання параметрів запиту, у даному випадку slug кімнати
            self.room_slug = self.scope['url_route']['kwargs']['room_slug']
            self.room = await self.get_room(user)

            # print('Connect to room:', room)
            # Приєднання до групи чату за допомогою slug кімнати
            await self.channel_layer.group_add(
                self.room_slug,
                self.channel_name
            )

        else:
            # Користувач не автентифікований, закрити з'єднання
            await self.close()

    async def disconnect(self, close_code):
        # Відключення клієнта
        await self.channel_layer.group_discard(
            self.room_slug,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        message = content.get('message')
        sender = content.get('sender')

        user = self.scope.get('user')
        add_message = await self.add_message(user, message)

        if add_message:
            # Відправка повідомлення в групу чату
            await self.channel_layer.group_send(
                self.room_slug,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender
                }
            )
        else:
            # Відправка помилки відправлення
            print('Sending error')
            pass

    async def chat_message(self, event):
        message = event.get('message')
        sender = event.get('sender')

        # Відправка повідомлення клієнту
        await self.send_json({
            'type': 'chat_message',
            'sender': sender,
            'message': message
        })
