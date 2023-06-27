import requests
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import generics, status, viewsets, mixins
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.views import APIView

from .models import ChatRoom, ChatMessage, UserProfile
from .serializers import *


class APIListPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatRoomsList(generics.ListAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsListSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = APIListPaginator

    def get(self, request, *args, **kwargs):
        chatRoom_slug = kwargs.get('room_slug', None)
        if chatRoom_slug:
            chat_room = get_object_or_404(ChatRoom, slug=chatRoom_slug)
            response_dict = {
                'name': chat_room.name,
                'slug': chat_room.slug,
                'messages': list(chat_room.messages.all().values('sender', 'message', 'time_send'))
            }
            return Response(response_dict)
        elif 'list' in request.path:
            return super().get(request, *args, **kwargs)

        return HttpResponseNotFound({'error': 'The path does not exist'})


class ChatRoomsCreate(generics.CreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsCreateSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Chat room created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatRoomsDelete(generics.DestroyAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsListSerializer
    lookup_field = 'room_slug'
    permission_classes = (IsAuthenticated,)

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializers
    permission_classes = [IsAdminUser]
    pagination_class = APIListPaginator
    lookup_field = 'username'




# class DeviceLogoutView(APIView):
#     def post(self, request):
#         user = request.user
#         user.auth_token.delete()
#         return Response(status=status.HTTP_200_OK)

