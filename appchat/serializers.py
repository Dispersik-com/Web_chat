from rest_framework import serializers
from .models import ChatRoom, UserProfile


class ChatRoomsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"


class ChatRoomsCreateSerializer(serializers.Serializer):
    Name = serializers.CharField(max_length=200)
    Is_private = serializers.BooleanField()
    Invite_users = serializers.CharField(required=False)
    Message_for_invite = serializers.CharField(required=False)

    def create(self, validated_data):
        room_name = validated_data.get('Name', None)
        is_private = validated_data.get('Is_private')
        invites = validated_data.get('invite_users', None)
        message = validated_data.get('Message_for_invite', None)
        if room_name is not None:
            Room = ChatRoom.create_chat_room(room_name, private=is_private)
            user_obj = UserProfile.objects.get(username=self.context['request'].user.username)
            user_obj.join_chatroom(Room)
            Room.users_in_chatroom.add(user_obj)

            if invites:
                user_obj.send_invite(invites.split(' '), {'room_slug': Room.slug, 'messages': message})

            return Room
        else:
            raise serializers.ValidationError("Invalid data")


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserCreateSerializer(serializers.Serializer):
    User_name = serializers.CharField(max_length=200)
    Email = serializers.CharField(max_length=200)
    Password = serializers.CharField(max_length=200)

    def create(self, validated_data):
        user_name = validated_data.get('User_name', None)
        email = validated_data.get('Email', None)
        password = validated_data.get('Password', None)
        if user_name and email and password:
            user = UserProfile.objects.create_user(username=user_name,
                                            password=password,
                                            email=email)
            return user
        else:
            raise serializers.ValidationError("Invalid data")