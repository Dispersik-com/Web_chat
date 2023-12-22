from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django import forms
from .models import *


class LoginFormView(LoginView):
    template_name = 'appchat/login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        login(self.request, form.get_user())
        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)
        else:
            return redirect(reverse_lazy('profile', kwargs={'user_name': self.request.user.username}))


class SingUpForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    username = forms.CharField(label='Login', max_length=255)
    email = forms.CharField(label='Email', max_length=255)
    password = forms.PasswordInput(render_value=True)
    password_valid = forms.PasswordInput(render_value=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_valid = cleaned_data.get('password_valid')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if UserProfile.objects.filter(Q(username=username) | Q(email=email)).exists():
            raise forms.ValidationError('This mail or username is already taken')

        if password and password_valid and password != password_valid:
            raise forms.ValidationError("Passwords do not match")

        if len(password) < 8:
            raise forms.ValidationError("Passwords must be 8 characters or more")

        return cleaned_data

    def save_to_db(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        User = UserProfile
        try:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_public_name=username,
                about='',
            )
            return True
        except Exception as e:
            print(e)
            return False


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo']


class CreateRoomForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    room_name = forms.CharField(label='Room name', max_length=100)
    invite_users = forms.CharField(label='Invite users', required=False)
    messages_for_invite = forms.CharField(label='Message for invite`s user', max_length=256, required=False)
    is_private = forms.BooleanField(label='Private room', required=False)

    def clean(self):
        cleaned_data = super().clean()
        room_name = cleaned_data.get('room_name')
        invite_users = cleaned_data.get('invite_users')
        messages_for_invite = cleaned_data.get('messages_for_invite')
        is_private = cleaned_data.get('is_private')

        if invite_users is not None:
            invites = invite_users.split(' ')
        else:
            invites = []

        self.cleaned_data['room_data'] = {
            'room_name': room_name,
            'private': is_private,
            'messages': messages_for_invite,
            'invite_users': invites,
        }

    def save_to_db(self):
        room_data = self.cleaned_data.get('room_data')

        Room = ChatRoom.create_chat_room(room_data['room_name'], private=room_data['private'])
        room_data['room_slug'] = Room.slug
        if Room:
            if self.request is None:
                return False
            user_obj = UserProfile.objects.get(username=self.request.user.username)
            user_obj.join_chatroom(Room)
            Room.users_in_chatroom.add(user_obj)

            invites = room_data['invite_users']
            notification = Notification(user=self,
                                        link=Room.get_absolute_url(),
                                        message=room_data.get('messages'))
            notification.save()
            if invites:
                user_obj.send_invite(invites, notification)

            return True
        else:
            return False


def form_manage(request, form_as=None):
    if form_as is not None:
        if request.method == 'POST':
            form = form_as(request.POST, request=request)
            if form.is_valid():
                if form.save_to_db():
                    return True
                else:
                    return False
            else:
                return form
        else:
            form = form_as()  # якщо метод запиту GET, то створюємо порожній об'єкт форми
            return form
    else:
        return None