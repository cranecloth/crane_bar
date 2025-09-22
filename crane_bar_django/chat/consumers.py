import json
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

API_URL = "https://openai.qiniu.com/v1/chat/completions"
API_KEY = "sk-4ad6e020dfcb77fb3cf4e0a209816b67373578b43d30e09d411ba59e57554bd5"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.role_name = self.scope["url_route"]["kwargs"]["role_name"]
        await self.accept()
        await self.send(text_data=json.dumps({
            "sender": self.role_name,
            "message": f"你好，我是 {self.role_name}，和我聊聊吧！"
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("message", "")

        # 调用外部 API (同步 -> 异步)
        reply = await sync_to_async(self.ask_ai)(user_message)

        await self.send(text_data=json.dumps({
            "sender": self.role_name,
            "message": reply
        }))

    def ask_ai(self, user_message: str) -> str:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "stream": False,
            "model": "deepseek-v3",
            "messages": [
                {
                    "role": "system",
                    "content": f"You are now roleplaying as {self.role_name}."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            # deepseek-v3 的返回格式类似 OpenAI
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[错误] AI 接口调用失败: {e}"
