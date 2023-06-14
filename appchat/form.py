
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django import forms
from .models import *
import hashlib
import time

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


class sing_up_form(forms.Form):
    username = forms.CharField(label='Login', max_length=255)
    email = forms.CharField(label='Email', max_length=255)
    password = forms.CharField(label='Password (first)', max_length=40)
    password_valid = forms.CharField(label='Password (valid)', max_length=40)

    new_user = {}

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_valid = cleaned_data.get('password_valid')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        self.new_user['username'] = username
        self.new_user['email'] = email
        self.new_user['password'] = password

        if UserProfile.objects.filter(Q(username=username) | Q(email=email)).exists():
            raise forms.ValidationError('This mail or username is already taken')

        if password and password_valid and password != password_valid:
            raise forms.ValidationError("Passwords do not match")

        if len(password) < 8:
            raise forms.ValidationError("Passwords must be 8 characters or more")

    def save_to_db(self):
        User = get_user_model()
        user = User.objects.create_user(
            username=self.new_user.get('username'),
            email=self.new_user.get('email'),
            password=self.new_user.get('password'),
            user_public_name=self.new_user.get('username'),
            about='',
        )
        if user:
            return True
        else:
            return False

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo']


class CreateRoomForm(forms.Form):
    room_name = forms.CharField(label='Room name', max_length=100)
    invite_users = forms.CharField(label='invite users', required=False)
    messages_for_invite = forms.CharField(label='Message for invite`s user', max_length=256, required=False)
    is_private = forms.BooleanField(label='Privet room', required=False)

    New_room = {}


    def clean(self):
        cleaned_data = super().clean()
        room_name = cleaned_data.get('room_name')
        invite_users = cleaned_data.get('invite_users')
        messages = cleaned_data.get('messages_for_invite')
        is_private = cleaned_data.get('is_private')

        self.New_room['room_name'] = room_name
        self.New_room['private'] = bool(is_private)
        self.New_room['messages'] = messages
        self.New_room['invite_users'] = invite_users


    def save_to_db(self):
        Room = ChatRoom.create_chat_room(self.New_room.get('room_name'),
                                         private=self.New_room.get('private'))
        user_obj = UserProfile.objects.get(username=self.cleaned_data.get('username'))
        user_obj.join_chat_room(Room)
        Room.users_in_chatroom.add(user_obj)
        self.New_room['room_slug'] = Room.slug
        invites = self.New_room.get('invite_users')
        if invites is not None:
            invates = invites.split(' ')
            user_obj.send_invite(invates, self.New_room)

        if Room:
            return True
        else:
            return False

def form_manage(request, form_as=None):
    if form_as is not None:
        if request.method == 'POST':
            form = form_as(request.POST)
            if form.is_valid():
                form.cleaned_data['username'] = request.user.username
                if form.save_to_db():
                    return True
            else:
                return form
        else:
            form = form_as()  # если метод запроса GET, то создаем пустой объект формы
            return form
    else:
        return None