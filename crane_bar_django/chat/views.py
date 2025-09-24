from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import ChatRecord, Character
from .serializers import ChatRecordSerializer, CharacterSerializer


class SaveChatView(APIView):
    def post(self, request):
        # 处理嵌套的 character 对象
        data = request.data.copy()
        
        # 如果存在 character 对象，提取其字段
        if 'character' in data and isinstance(data['character'], dict):
            character = data.pop('character')
            # 映射字段
            field_mapping = {
                'character_name': 'character_name', 
                'description': 'character_description',
                'temperature': 'temperature',
                'greeting':'greeting',
                'top_p': 'top_p',
                'top_k': 'top_k'
            }
            
            for char_key, data_key in field_mapping.items():
                if char_key in character:
                    data[data_key] = character[char_key]
        
        # 过滤允许的字段
        allowed_fields = [
            'user_id', 'title', 'content',
            'character_id', 'character_name', 'character_description','greeting',
            'temperature', 'top_p', 'top_k'
        ]
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        serializer = ChatRecordSerializer(data=filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            chat = ChatRecord.objects.get(pk=request.data.get('id'))
            data = request.data.copy()
            
            # 同样的处理逻辑
            if 'character' in data and isinstance(data['character'], dict):
                character = data.pop('character')
                field_mapping = {
                    'id': 'character_id',
                    'character_name': 'character_name',
                    'description': 'character_description',
                    'temperature': 'temperature',
                    'greeting':'greeting',
                    'top_p': 'top_p',
                    'top_k': 'top_k'
                }
                
                for char_key, data_key in field_mapping.items():
                    if char_key in character:
                        data[data_key] = character[char_key]
            
            allowed_fields = [
                'user_id', 'title', 'content',
                'character_name', 'character_description','greeting',
                'temperature', 'top_p', 'top_k'
            ]
            filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

            serializer = ChatRecordSerializer(chat, data=filtered_data, partial=True)
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
    """获取用户的聊天记录列表"""
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id parameter is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        chats = ChatRecord.objects.filter(user_id=user_id).order_by('-updated_at')
        serializer = ChatRecordSerializer(chats, many=True)
        return Response(serializer.data)


class ChatDetailView(APIView):
    """单个聊天的详情/删除/更新"""
    def get(self, request, user_id, chat_id):
        chat = get_object_or_404(ChatRecord, pk=chat_id, user_id=user_id)
        return Response(ChatRecordSerializer(chat).data)

    def delete(self, request, user_id, chat_id):
        chat = get_object_or_404(ChatRecord, pk=chat_id, user_id=user_id)
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, user_id, chat_id):
        chat = get_object_or_404(ChatRecord, pk=chat_id, user_id=user_id)
        serializer = ChatRecordSerializer(chat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CharacterListView(generics.ListCreateAPIView):
    """列出所有角色，或新建自定义角色"""
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer


class CharacterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """查看/修改/删除角色"""
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
