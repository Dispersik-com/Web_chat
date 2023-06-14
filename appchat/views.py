from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.forms import forms
# from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
# from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session

from .form import sing_up_form, CreateRoomForm, form_manage, UserProfileForm
from .models import *


# Стартовая страница
def index(request):
    if request.user.is_authenticated:
        return redirect('profile', user_name=request.user.usrname)
    return render(request, 'appchat/index.html')

def sing_up_view(request):
    form = form_manage(request, form_as=sing_up_form)

    context = {}

    if isinstance(form, forms.Form):
        context = {'form': form}
    elif form is True:
        return render(request, 'appchat/thanks_page.html')

    return render(request, 'appchat/Sing_up.html', context=context)

# Для использования logout нужно дать ссылку на модель в settings.py в поле AUTH_USER_MODEL
def logout_view(request):
    logout(request)
    return render(request, 'appchat/index.html')


class DataMixin:
    """ Класс для получения общих данных и уменьшения количества кода"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получить количество активных пользователей
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        active_users_count = active_sessions.count()
        context['active_users_count'] = active_users_count

        return context

# Декоратор метода отправки (name='dispatch'), для проверки авторизации пользователя (login_required)
@method_decorator(login_required, name='dispatch')
class GlobalRoom(DataMixin, ListView):
    model = ChatRoom
    template_name = 'appchat/global_room.html'
    context_object_name = 'page_obj'
    paginate_by = 10


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['per_page'] = self.paginate_by
        return context

    def get_queryset(self):
        queryset = super().get_queryset().order_by('time_created')
        # Создание постраничной навигации
        per_page = self.request.GET.get('per_page', self.paginate_by)
        paginator = Paginator(queryset, per_page)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return page_obj


@method_decorator(login_required, name='dispatch')
class ProfileDetailView(DataMixin, DetailView):
    model = UserProfile
    template_name = 'appchat/profile.html'
    # context_object_name = 'user_profile'
    slug_url_kwarg = 'user_name'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.user.username
        another_username = self.request.path.split('/')[-1]
        context['profile_another_user'] = username != another_username
        return context

    def get(self, request, *args, **kwargs):
        # Проверка условия для переадресации
        username = request.user.username
        another_username = request.path.split('/')[-1]
        if username != another_username:
            return redirect('another_profile', user_name=username, another_username=another_username)

        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        user = self.get_object()

        # Обработка загрузки фотографии
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

        # Обработка других полей профиля
        user.user_public_name = request.POST.get('public-name')
        user.about = request.POST.get('about-me')
        user.save()

        return self.get(request, *args, **kwargs)

class ProfileAnotherUserView(DataMixin, DetailView):
    model = UserProfile
    template_name = 'appchat/profile.html'
    slug_url_kwarg = 'user_name'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        another_username = self.request.path.split('/')[-1]
        context['profile_another_user'] = True
        context['obj_another_user'] = UserProfile.objects.get(username=another_username)
        return context


def add_friend(request, user_name, another_username):
    user_obj = UserProfile.objects.get(username=user_name)
    friend_obj = UserProfile.objects.get(username=another_username)

    if user_obj != friend_obj:
        user_obj.friends.add(friend_obj)
        user_obj.save()

    path = str(request.path).replace('addfriend/', '')
    return redirect(path)


@method_decorator(login_required, name='dispatch')
class ChatRoomDetailView(DataMixin, DetailView):
    model = ChatRoom
    template_name = 'appchat/chat_room.html'
    context_object_name = 'chat_room'
    slug_url_kwarg = 'room_slug'

    def post(self, request, *args, **kwargs):
        chat_room = self.get_object()
        message = request.POST.get('message')
        sender = request.user

        if message and sender:
            chat_room.add_message(sender, message)

            # Создание и возврат JSON-ответа с добавленным сообщением
            new_message = ChatMessage.objects.latest('time_send')
            response_data = {
                'message': {
                    'sender': {
                        'username': new_message.sender.username
                    },
                    'message': new_message.message
                }
            }
            return JsonResponse(response_data)

        return super().get(request, *args, **kwargs)

@login_required
def create_chatRoom(request):
    form = form_manage(request, form_as=CreateRoomForm)

    context = {'created': False}

    if isinstance(form, forms.Form):
        context = {'form': form }
    elif form is True:
        Success_message = f'The room "{request.POST.get("room_name")}" has been successfully created and added to your list of rooms.'
        context = {'Success_message': Success_message}
        context['created'] = True

    return render(request, 'appchat/create_chatRoom.html', context=context)

@login_required
@require_POST # декоратор, который разрешает работу функции только, если метод запроса - POST
def join_the_room(request, room_slug):
    user = UserProfile.objects.get(username=request.user)
    room = ChatRoom.objects.get(slug=room_slug)
    user.join_chat_room(room)
    return HttpResponseRedirect(reverse('chat_room', args=[room_slug]))

@method_decorator(login_required, name='dispatch')
class NotificationsView(ListView):
    model = Notification
    template_name = 'appchat/notifications.html'
    context_object_name = 'notifications'

@login_required
@require_POST
def delete_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.delete()
    return HttpResponseRedirect('/notifications/')

@login_required
def leave_room(request, room_slug):
    username = request.user.username
    chat_room = ChatRoom.objects.get(slug=room_slug)
    user = UserProfile.objects.get(username=username)
    user.leave_chat_room(chat_room)
    count_user = chat_room.user_count - 1
    if count_user <= 0:
        # Удаляем все сообщения которые ассоциируются в этой чат-комнатой
        chat_room.messages.all().delete()
        # Удаляем запись из таблицы о комнате
        chat_room.delete()
    else:
        chat_room.user_count = count_user

    chat_room.save()

    return redirect('profile', user_name=request.user.username)

# Обработка 404, обязательно добавить ссылку на функцию в urls.py
def pageNotFound(request, exception):
    return render(request, 'appchat/pageError.html')

