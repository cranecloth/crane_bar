from rest_framework import serializers
from .models import ChatRecord, Character


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = [
            'id',
            'name',
            'role_type',
            'description',
            'temperature',
            'top_p',
            'top_k',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRecord
        fields = [
            'id',
            'user_id',
            'title',
            'content',
            'character_id',
            'character_name',
            'character_description',
            'greeting',
            'temperature',
            'top_p',
            'top_k',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
