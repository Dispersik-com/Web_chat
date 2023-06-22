from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from .models import ChatRoom, ChatMessage, UserProfile
from .serializers import *

class ChatRoomsList(generics.ListAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsListSerializer
    pagination_class = PageNumberPagination
    # permission_classes = (IsAuthenticated, )
    page_size = 20
    page_size_query_param = 'page_size'

    def get(self, request, *args, **kwargs):
        chatRoom_slug = kwargs.get('chatRoom_slug', None)
        if chatRoom_slug:
            chat_room = get_object_or_404(ChatRoom, slug=chatRoom_slug)
            response_dict = {
                'name': chat_room.name,
                'slug': chat_room.slug,
                'messages': list(chat_room.messages.all().values('username', 'message', 'time_send'))
            }
            return Response(response_dict)
        elif 'List' in request.path:
            return super().get(request, *args, **kwargs)

        return HttpResponseNotFound({'error': 'The path does not exist'})


class ChatRoomsCreate(generics.CreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsCreateSerializer
    pagination_class = PageNumberPagination
    # permission_classes = (IsAuthenticated,)

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
    lookup_field = 'slug'
    # permission_classes = (IsAuthenticated,)




# class DeviceLogoutView(APIView):
#     def post(self, request):
#         user = request.user
#         user.auth_token.delete()
#         return Response(status=status.HTTP_200_OK)

