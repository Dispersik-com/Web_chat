import unittest

from django.test import TestCase
from django.urls import reverse
from .models import UserProfile, ChatRoom, ChatMessage, Notification


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='testpass')

    def test_create_user(self):
        self.assertIsInstance(self.user, UserProfile)
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_create_superuser(self):
        admin_user = UserProfile.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.assertIsInstance(admin_user, UserProfile)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_get_friends(self):
        # Test getting friends for the user
        friend1 = UserProfile.objects.create_user(username='friend1', email='friend1@example.com', password='friend1pass')
        friend2 = UserProfile.objects.create_user(username='friend2', email='friend2@example.com', password='friend2pass')
        self.user.friends.add(friend1)
        self.user.friends.add(friend2)
        self.assertEqual(self.user.get_friends().count(), 2)

    def test_send_invite(self):
        # Test sending an invite and creating a notification
        chat_room = ChatRoom.create_chat_room(name='Test Room')
        recipients = ['user1', 'user2', 'user3']
        recipients_obj = []
        for user in recipients:
            temp_user = UserProfile.objects.create_user(username=user, email=f'{user}@example.com', password='testpass')
            recipients_obj.append(temp_user)

        notification = Notification.objects.create(user=self.user, link=chat_room.get_absolute_url(),
                                                   message='test message')

        self.user.send_invite(recipients, notification)

        for recipient in recipients_obj:
            # Получаем уведомление для каждого получателя
            recipient_notification = recipient.notifications.all()[0]
            # Проверяем, что уведомление совпадает с созданным уведомлением
            self.assertEqual(recipient_notification, notification)

    def test_join_and_leave_chatroom(self):
        # Test joining and leaving a chat room
        chat_room = ChatRoom.create_chat_room(name='Test Room')
        self.user.join_chatroom(chat_room)
        self.assertEqual(chat_room.user_count, 1)
        self.assertEqual(self.user.chat_rooms.count(), 1)

        self.user.leave_chatroom(chat_room)
        self.assertEqual(chat_room.user_count, 0)
        self.assertEqual(self.user.chat_rooms.count(), 0)


class ChatRoomTestCase(TestCase):
    def test_create_chat_room(self):
        # Test creating a chat room
        chat_room = ChatRoom.create_chat_room(name='Test Room')
        self.assertIsInstance(chat_room, ChatRoom)
        self.assertEqual(ChatRoom.objects.count(), 1)

    def test_add_message(self):
        # Test adding a message to a chat room
        chat_room = ChatRoom.create_chat_room(name='Test Room')
        user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        message = "Test message"
        chat_room.add_message(user, message)
        self.assertEqual(chat_room.messages.count(), 1)
        self.assertEqual(chat_room.get_messages()[0].message, message)


class ChatMessageTestCase(TestCase):
    def test_get_message(self):
        # Test getting a chat message
        user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        message_text = "Test message"
        message = ChatMessage.objects.create(sender=user, message=message_text)
        self.assertEqual(message.get_message(), [message_text])


class NotificationTestCase(TestCase):
    def test_notification_creation(self):
        # Test creating a notification
        user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        notification = Notification.objects.create(user=user, link='test_link', message='Test message')
        self.assertIsInstance(notification, Notification)
        self.assertEqual(Notification.objects.count(), 1)


class UserProfileManagerTestCase(TestCase):
    def test_create_user(self):
        # Test creating a user through the manager
        manager = UserProfile.objects
        user = manager.create_user(username='testuser', email='test@example.com', password='testpass')
        self.assertIsInstance(user, UserProfile)
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_create_superuser(self):
        # Test creating a superuser through the manager
        manager = UserProfile.objects
        admin_user = manager.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.assertIsInstance(admin_user, UserProfile)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)


class ChatRoomModelTestCase(TestCase):
    def test_get_absolute_url(self):
        # Test getting the absolute URL for the chat room
        chat_room = ChatRoom.create_chat_room(name='Test Room')
        self.assertEqual(chat_room.get_absolute_url(), reverse('chat_room', args=[chat_room.slug]))


if __name__ == '__main__':
    unittest.main()
