from django import template
from datetime import datetime

from appchat.models import *

register = template.Library()

@register.simple_tag
def in_chat_room(username, room):
    slug_room = room.split('/')[-2]
    chat_room = ChatRoom.objects.get(slug=slug_room)
    users_in_chatroom_list = list(chat_room.users_in_chatroom.all().values_list('username', flat=True))
    return username in users_in_chatroom_list


@register.simple_tag
def is_friends(user, obj_another_user):
    return user in list(obj_another_user.friends.all())


