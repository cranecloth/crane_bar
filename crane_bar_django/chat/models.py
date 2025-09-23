from django.db import models
from django.utils import timezone

class Character(models.Model):
    ROLE_CHOICES = [
        ('harry', '哈利波特'),
        ('socrates', '苏格拉底'),
        ('custom', '自定义')
    ]
    
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES)
    description = models.TextField()
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=0.9)
    top_k = models.IntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ChatRecord(models.Model):
    user_id = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    content = models.JSONField()
    character = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.user_id})"
