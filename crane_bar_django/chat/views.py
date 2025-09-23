from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import ChatRecord, Character
from .serializers import ChatRecordSerializer, CharacterSerializer
import json

class SaveChatView(APIView):
    def post(self, request):
        serializer = ChatRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            chat = ChatRecord.objects.get(pk=request.data.get('id'))
            serializer = ChatRecordSerializer(chat, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRecord.DoesNotExist:
            return Response(
                {"error": "Chat record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class ChatListView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chats = ChatRecord.objects.filter(user_id=user_id).order_by('-updated_at')
        serializer = ChatRecordSerializer(chats, many=True)
        return Response(serializer.data)

class ChatDetailView(APIView):
    def get(self, request, user_id, chat_id):
        try:
            chat = ChatRecord.objects.get(pk=chat_id, user_id=user_id)
            serializer = ChatRecordSerializer(chat)
            return Response(serializer.data)
        except ChatRecord.DoesNotExist:
            return Response(
                {"error": "Chat record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, user_id, chat_id):
        try:
            chat = ChatRecord.objects.get(pk=chat_id, user_id=user_id)
            chat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ChatRecord.DoesNotExist:
            return Response(
                {"error": "Chat record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, user_id, chat_id):
        try:
            chat = ChatRecord.objects.get(pk=chat_id, user_id=user_id)
            serializer = ChatRecordSerializer(chat, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ChatRecord.DoesNotExist:
            return Response(
                {"error": "Chat record not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class CharacterListView(generics.ListCreateAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer

class CharacterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
