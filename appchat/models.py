import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from pytils.translit import slugify


class UserProfileManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        # Перевіряємо, чи надано ім'я користувача
        if not username:
            raise ValueError('Поле імені користувача повинно бути заповненим')
        # Створюємо новий екземпляр користувача з наданим ім'ям користувача та будь-якими додатковими полями
        user = self.model(username=username, **extra_fields)
        # Встановлюємо пароль користувача
        user.set_password(password)
        # Зберігаємо об'єкт користувача у базі даних
        user.save(using=self._db)
        # Повертаємо створеного користувача
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        # За замовчуванням встановлюємо значення полів 'is_staff' і 'is_superuser' в True у словнику extra_fields
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Створюємо суперкористувача, використовуючи метод create_user
        # з наданим ім'ям користувача, паролем і додатковими полями
        return self.create_user(username, password, **extra_fields)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    user_public_name = models.CharField(max_length=255)
    session_id = models.CharField(max_length=65)
    photo = models.ImageField(upload_to="UserFace/", default='default/default-user-image.png')
    chat_rooms = models.ManyToManyField('ChatRoom')
    notifications = models.ManyToManyField('Notification')
    about = models.TextField()
    friends = models.ManyToManyField('self', symmetrical=False)
    date_sing_in = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Створення екземпляра UserProfileManager для управління профілями користувачів
    objects = UserProfileManager()

    # Вказання поля імені користувача, що використовується як унікальний ідентифікатор для аутентифікації
    USERNAME_FIELD = 'username'
    # Вказання обов'язкових полів для створення профілю користувача
    REQUIRED_FIELDS = ['email']

    def get_friends(self):
        return self.friends.all()

    def send_invite(self, recipients, notification):

        Users = UserProfile.objects.filter(username__in=recipients)
        for user in Users:
            user.notifications.add(notification)
            user.save()

    def get_notifications(self):
        return list(self.notifications.all())

    def join_chatroom(self, chat_room):
        self.chat_rooms.add(chat_room)
        chat_room.users_in_chatroom.add(self)
        chat_room.user_count = chat_room.users_in_chatroom.count()
        chat_room.save()
        self.save()

    def leave_chatroom(self, chat_room):
        self.chat_rooms.remove(chat_room)
        chat_room.user_count -= 1
        chat_room.users_in_chatroom.remove(self)
        self.save()


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    link = models.TextField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.TextField()
    time_send = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(f'{self.sender}: {self.message}')

    def get_message(self):
        return [self.message]


class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    messages = models.ManyToManyField('ChatMessage')
    users_in_chatroom = models.ManyToManyField('UserProfile')
    user_count = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

    def get_messages(self):
        return list(self.messages.all())

    def add_message(self, sender, message):
        try:
            new_message = ChatMessage(sender=sender, message=message)
            new_message.save()
            self.messages.add(new_message)
            self.save()
        except Exception:
            return False
        return new_message

    def get_absolute_url(self):
        return reverse('chat_room', args=[self.slug])


    @classmethod
    def create_chat_room(cls, name, private=False):
        try:
            slug = slugify(name)
            slug_suffix = hash(datetime.datetime.now().isoformat())
            slug = f"{slug}_{slug_suffix}"
            # Створюємо об'єкт кімнати чату
            chat_room = cls(name=name, slug=slug, user_count=0, is_private=private)
            chat_room.save()
            return chat_room

        except Exception as e:
            raise ValueError(f"Chat room with name '{name}' - Error: {e}")
