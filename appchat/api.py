from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomsSerializer

class ChatRoomsListCreate(generics.ListCreateAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsSerializer
    pagination_class = PageNumberPagination
    # page_size = 20
    # page_size_query_param = 'page_size'

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

    def post(self, request, *args, **kwargs):
        chatRoom_slug = kwargs.get('chatRoom_slug', None)
        if chatRoom_slug and 'send' in request.path:
            chat_room = get_object_or_404(ChatRoom, slug=chatRoom_slug)
            new_message = ChatMessage(**kwargs)
            chat_room.messages.add(new_message)
            new_message.save()
            chat_room.save()
            return Response({'Response ': 'Message success append'})

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'post': serializer.data})


class ChatRoomsDelete(generics.DestroyAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomsSerializer
    lookup_field = 'slug'

    def perform_destroy(self, instance):
        return instance.delete()

