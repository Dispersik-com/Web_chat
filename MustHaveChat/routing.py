from django.urls import re_path, path
from appchat import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat_room/(?P<room_slug>[-\w]+)/$', consumers.ChatConsumer.as_asgi()),
]
