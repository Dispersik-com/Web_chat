from .views import *
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .form import LoginFormView
from django.views.decorators.cache import cache_page

from .api import *
from rest_framework import routers

urlpatterns = [
    path('', index, name='index'),
    path('sing_up/', sing_up_view, name='sing_up'),
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/<slug:user_name>', cache_page(60*3)(ProfileDetailView.as_view()), name='profile'),
    path('profile/<slug:user_name>/<slug:another_username>', cache_page(60*3)(ProfileAnotherUserView.as_view()), name='another_profile'),
    path('profile/addfriend/<slug:user_name>/<slug:another_username>', add_friend, name='add_friend'),
    path('chat_room/<slug:room_slug>/', ChatRoomDetailView.as_view(), name='chat_room'),
    path('chat_room/join/<slug:room_slug>/', join_the_room, name='join_the_room'),
    path('global_room/', GlobalRoom.as_view(), name='global_room'),
    path('create_chatRoom/', create_chatRoom, name='create_chatRoom'),
    path('leave_room/<slug:room_slug>', leave_room, name='leave_room'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Обязательно добавить для статических файлов


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

api_urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/create-user/', UserCreate.as_view()),
    path('api/v1/drf-auth/', include('rest_framework.urls')),
    path('api/v1/chat-rooms/list/', ChatRoomsList.as_view()),
    path('api/v1/chat-rooms/room/<slug:room_slug>/', ChatRoomsList.as_view()),
    path('api/v1/chat-rooms/create/', ChatRoomsCreate.as_view()),
    path('api/v1/chat-rooms/delete/<slug:room_slug>/', ChatRoomsDelete.as_view()),
]

urlpatterns += api_urlpatterns