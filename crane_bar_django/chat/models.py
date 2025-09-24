from django.db import models

class Character(models.Model):
    ROLE_CHOICES = [
        ('harry', '哈利波特'),
        ('socrates', '苏格拉底'),
        ('custom', '自定义')
    ]
    
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES, default='custom')
    description = models.TextField()
    greeting = models.TextField(default="你好，我可以为你做些什么？")
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=0.9)
    top_k = models.IntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_role_type_display()})"


from django.db import models

class ChatRecord(models.Model):
    user_id = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    # 前端传来的角色信息，纯文本保存
    character_id = models.CharField(max_length=100, blank=True, null=True)  
    character_name = models.CharField(max_length=100,default='')
    character_description = models.TextField(default='')
    greeting = models.TextField(default="你好，我可以为你做些什么？")
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=0.7)
    top_k = models.IntegerField(default=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title or self.character_name} - {self.user_id}"
