from django.contrib import admin
from .models import ChatRecord

@admin.register(ChatRecord)
class ChatRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_id', 'created_at', 'updated_at')
    search_fields = ('title', 'user_id')
    list_filter = ('created_at', 'updated_at')
