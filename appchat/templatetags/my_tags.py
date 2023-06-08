from django import template
from datetime import datetime

from appchat.models import *

register = template.Library()

@register.simple_tag
def in_chat_room(username):
    user = UserProfile.objects.get(username=username)
    chat_room = ChatRoom.objects.filter(users_in_chatroom=user)
    if chat_room.exists():
        return True
    else:
        return False




