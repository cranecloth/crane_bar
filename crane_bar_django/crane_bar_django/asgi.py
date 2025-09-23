import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

# 设置环境变量并初始化Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crane_bar_django.settings')

# 确保Django完全初始化
try:
    django_asgi_app = get_asgi_application()
    django.setup()
except Exception as e:
    raise RuntimeError(f"Django setup failed: {e}")

# 创建ASGI应用
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    )
})
