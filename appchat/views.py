from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.forms import forms
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.contrib.auth import logout
from django.shortcuts import render, redirect

from .utils import DataMixin
from .form import SingUpForm, CreateRoomForm, form_manage, UserProfileForm
from .models import *


# стартовая странница
def index(request):
    if request.user.is_authenticated:
        return redirect('profile', user_name=request.user.username)
    return render(request, 'appchat/index.html')


def sing_up_view(request):
    form = form_manage(request, form_as=SingUpForm)

    context = {}

    if isinstance(form, forms.Form):
        context = {'form': form}
    elif form is True:
        return render(request, 'appchat/thanks_page.html')
    elif form is False:
        return HttpResponseServerError(f"Internal Server Error")

    return render(request, 'appchat/Sing_up.html', context=context)


# Для использования logout нужно дать ссылку на модель в settings.py в поле AUTH_USER_MODEL
def logout_view(request):
    logout(request)
    return render(request, 'appchat/index.html')


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
        try:
            queryset = super().get_queryset().order_by('time_created')
            per_page = self.request.GET.get('per_page', self.paginate_by)
            paginator = Paginator(queryset, per_page)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return page_obj
        except Exception as e:
            # Обработка исключений
            print(f"An error occurred: {str(e)}")
            # Возвращение пустого QuerySet или другой логики обработки ошибок
            return ChatRoom.objects.none()


@method_decorator(login_required, name='dispatch')
class ProfileDetailView(DataMixin, DetailView):
    model = UserProfile
    template_name = 'appchat/profile.html'
    slug_url_kwarg = 'user_name'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.request.user.username
        another_username = self.request.path.split('/')[-1]
        context['profile_another_user'] = username != another_username
        return context

    def get(self, request, *args, **kwargs):
        username = request.user.username
        another_username = request.path.split('/')[-1]
        if username != another_username:
            return redirect('another_profile', user_name=username, another_username=another_username)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                return self.render_to_response(self.get_context_data(form=form))

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
        try:
            context['obj_another_user'] = UserProfile.objects.get(username=another_username)
        except ObjectDoesNotExist as e:
            # Обработка ошибки отсутствия пользователя
            print(f"User with username {another_username} does not exist: {str(e)}")
            # Возвращение ошибки или другая логика обработки ошибок
        return context


def add_friend(request, user_name, another_username):
    try:
        user_obj = UserProfile.objects.get(username=user_name)
        friend_obj = UserProfile.objects.get(username=another_username)

        if user_obj != friend_obj:
            user_obj.friends.add(friend_obj)
            user_obj.save()

        path = request.path.replace('addfriend/', '')
        return redirect(path)

    except ObjectDoesNotExist:
        # Обработка, если объект не существует
        # Перенаправление на страницу ошибки
        return render(request, 'error_page.html', {'error_message': 'User does not exist.'})

    except Exception as e:
        # Общий обработчик ошибок
        # Можно здесь записывать логи или принимать другие меры
        print(f"An error occurred: {str(e)}")
        # Перенаправление на страницу ошибки
        return render(request, 'error_page.html', {'error_message': f"An error occurred: {str(e)}"})



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
            # Создание и возврат JSON-ответа с добавленным сообщением
            new_message = chat_room.add_message(sender, message)
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
        context = {'form': form}
    elif form is True:
        success_message = f'The room "{request.POST.get("room_name")}" has been successfully created and added to ' \
                          f'your list of rooms.'
        context = {'Success_message': success_message,
                   'created': True}
    elif form is False:
        return HttpResponseServerError(f"Internal Server Error")

    return render(request, 'appchat/create_chatRoom.html', context=context)


@login_required
@require_POST  # декоратор, который разрешает работу функции, в случае если она имеет POST-запрос
def join_the_room(request, room_slug):
    try:
        user = UserProfile.objects.get(username=request.user)
        room = ChatRoom.objects.get(slug=room_slug)
        user.join_chatroom(room)
    except UserProfile.DoesNotExist:
        # Обработка отсутствия пользователя
        return HttpResponse('User does not exist')
    except ChatRoom.DoesNotExist:
        # Обработка отсутствия комнаты чата
        return HttpResponse('Chat room does not exist')
    except Exception as e:
        # Обработка других ошибок
        return HttpResponse(f'An error occurred: {str(e)}')

    return HttpResponseRedirect(reverse('chat_room', args=[room_slug]))


@method_decorator(login_required, name='dispatch')
class NotificationsView(ListView):
    template_name = 'appchat/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        try:
            user = self.request.user
            queryset = user.notifications.all()
            return queryset
        except Exception as e:
            # Обработка ошибок получения уведомлений
            return []


@login_required
@require_POST
def delete_notification(request, notification_id):
    try:
        user = UserProfile.objects.get(username=request.user.username)
        notification = Notification.objects.get(id=notification_id)
        user.notifications.remove(notification)
    except UserProfile.DoesNotExist:
        # Обработка отсутствия пользователя
        return HttpResponse('User does not exist')
    except Notification.DoesNotExist:
        # Обработка отсутствия уведомления
        return HttpResponse('Notification does not exist')
    except Exception as e:
        # Обработка других ошибок
        return HttpResponse(f'An error occurred: {str(e)}')

    return HttpResponseRedirect('/notifications/')


@login_required
def leave_room(request, room_slug):
    username = request.user.username
    chat_room = ChatRoom.objects.get(slug=room_slug)
    user = UserProfile.objects.get(username=username)
    user.leave_chatroom(chat_room)
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
def page_not_found(request, exception):
    context = {"error_message": exception}
    return render(request, 'appchat/error_page.html', context=context)


def error_500_view(request):
    context = {
        'error_message': 'Internal Server Error',
        'error_code': 500
    }
    return render(request, 'error_page.html', context)
