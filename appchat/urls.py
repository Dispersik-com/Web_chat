from .views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .form import LoginFormView

urlpatterns = [
    path('', index, name='index'),
    path('sing_up/', sing_up_view, name='sing_up'),
    path('login/', LoginFormView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/<slug:user_name>', ProfileDetailView.as_view(), name='profile'),
    path('profile/<slug:user_name>/<slug:friend>', add_friend, name='add_friend'),
    path('chat_room/<slug:room_slug>/', ChatRoomDetailView.as_view(), name='chat_room'),
    path('chat_room/join/<slug:room_slug>/', join_the_room, name='join_the_room'),
    path('global_room/', GlobalRoom.as_view(), name='global_room'),
    path('create_chatRoom/', create_chatRoom, name='create_chatRoom'),
    path('leave_room/<slug:room_slug>', leave_room, name='leave_room'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Обязательно добавить для статических файлов
