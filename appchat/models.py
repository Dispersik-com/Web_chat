import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from pytils.translit import slugify


# Create your models here.
"""
AbstractBaseUser - Этот класс предоставляет абстрактную реализацию модели пользователя 
и определяет минимальный набор функций, необходимых для работы с системой аутентификации. 
Он служит основой для создания пользовательской модели, заменяя стандартную модель пользователя Django. 
В коде, класс UserProfile наследуется от AbstractBaseUser, чтобы определить пользовательскую модель.

PermissionsMixin - Этот класс добавляет поле и методы, связанные с разрешениями и правами доступа, 
к модели пользователя. 
Он предоставляет удобные методы для проверки разрешений пользователя, 
определения его статуса администратора и других связанных функций. 
В коде, класс UserProfile наследуется от PermissionsMixin, 
чтобы добавить разрешения и функции управления доступом к пользовательской модели.

BaseUserManager - Этот класс предоставляет базовую функциональность для создания, 
изменения и удаления пользователей. 
Он содержит методы для создания обычных пользователей и суперпользователей. 
Менеджер модели пользователя, в данном случае UserProfileManager, 
наследуется от BaseUserManager для определения специфичной логики создания и управления пользователями.

"""


class UserProfileManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        # Проверяем, предоставлено ли имя пользователя
        if not username:
            raise ValueError('The Username field must be set')
        # Создаем новый экземпляр пользователя с предоставленным именем пользователя и любыми дополнительными полями
        user = self.model(username=username, **extra_fields)
        # Устанавливаем пароль пользователя
        user.set_password(password)
        # Сохраняем объект пользователя в базе данных
        user.save(using=self._db)
        # Возвращаем созданного пользователя
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        # По умолчанию устанавливаем значения полей 'is_staff' и 'is_superuser' в True в словаре extra_fields
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Создаем суперпользователя, используя метод create_user
        # с предоставленным именем пользователя, паролем и дополнительными полями
        return self.create_user(username, password, **extra_fields)

class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    user_public_name = models.CharField(max_length=255)
    session_id = models.CharField(max_length=65)
    photo = models.ImageField(upload_to="UserFace/", default='appchat/image/default-user-image.png')
    chat_rooms = models.ManyToManyField('ChatRoom')
    notifications = models.ManyToManyField('Notification')
    about = models.TextField()
    friends = models.ManyToManyField('self')
    date_sing_in = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Создание экземпляра UserProfileManager для управления профилями пользователей
    objects = UserProfileManager()

    # Указание поля имени пользователя, используемого в качестве уникального идентификатора для аутентификации
    USERNAME_FIELD = 'username'
    # Указание обязательных полей для создания профиля пользователя
    REQUIRED_FIELDS = ['email']

    def get_friends(self):
        return self.friends.all()

    def send_invite(self, recipients, room):
        Users = UserProfile.objects.filter(username__in=recipients)
        notification = Notification(user=self,
                                    link=room.get('room_slug'),
                                    message=room.get('messages'))
        notification.save()
        for user in Users:
            user.notifications.add(notification)
            user.save()


    def join_chat_room(self, chat_room):
        self.chat_rooms.add(chat_room)
        chat_room.users_in_chatroom.add(self)
        chat_room.save()
        self.save()

    def leave_chat_room(self, chat_room):
        self.chat_rooms.remove(chat_room)
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

    # def get_sender(self):
    #     return [self.sender]

    def get_message(self):
        return [self.message]


class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    messages = models.ManyToManyField('ChatMessage')
    users_in_chatroom = models.ManyToManyField('UserProfile')
    user_count = models.PositiveIntegerField()
    is_private = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)

    def get_messages(self):
        return list(self.messages.all())

    def add_message(self, sender, message):
        new_message = ChatMessage(sender=sender, message=message)
        new_message.save()
        self.messages.add(new_message)
        self.save()

    def get_absolute_url(self):
        return reverse('chat_room', args=[self.slug])


    @classmethod
    def create_chat_room(cls, name, private=False):
        try:
            # Формируем уникальный slug для комнаты
            slug = slugify(name)
            slug_suffix = hash(datetime.datetime.now().isoformat())
            slug = f"{slug}-{slug_suffix}"
            # Создаем объект комнаты чата
            chat_room = cls(name=name, slug=slug, user_count=1, is_private=private)
            chat_room.save()
            return chat_room

        except Exception as e:
            raise ValueError(f"Chat room with name '{name}' - Error: {e}")
