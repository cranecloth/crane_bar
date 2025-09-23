from rest_framework import serializers
from .models import ChatRecord, Character

class ChatRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = ['id', 'user_id', 'title', 'content', 'created_at', 'updated_at']

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'name', 'description', 'temperature', 'top_p', 'top_k', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
