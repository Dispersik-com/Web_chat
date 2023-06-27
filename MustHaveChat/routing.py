from django.urls import re_path
from appchat.consumers import ChatConsumer
from channels.auth import AuthMiddlewareStack

websocket_urlpatterns = [
    re_path(r'ws/chat_room/(?P<room_slug>[-\w]+)/$', AuthMiddlewareStack(ChatConsumer.as_asgi())),
]