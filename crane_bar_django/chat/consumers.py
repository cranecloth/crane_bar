import json
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

API_URL = "https://openai.qiniu.com/v1/chat/completions"
API_KEY = "sk-4ad6e020dfcb77fb3cf4e0a209816b67373578b43d30e09d411ba59e57554bd5"  # 建议放到环境变量里，而不是写死


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_id = None
        self.character = None

    async def connect(self):
        from .models import ChatRecord, Character

        self.chat_id = self.scope["url_route"]["kwargs"].get("chat_id")
        await self.accept()

        try:
            # 预设角色
            preset_characters = [
                {
                    'name': '哈利波特',
                    'description': '霍格沃茨的学生，擅长魔法和魁地奇',
                    'temperature': 0.7,
                    'top_p': 0.9,
                },
                {
                    'name': '苏格拉底',
                    'description': '古希腊哲学家，以提问和对话著称',
                    'temperature': 0.5,
                    'top_p': 0.8,
                },
                {
                    'name': '助手',
                    'description': '乐于助人的AI助手',
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            ]

            # 创建或更新预设角色
            for char_data in preset_characters:
                await sync_to_async(Character.objects.update_or_create)(
                    name=char_data['name'],
                    defaults=char_data
                )

            # 如果 chat_id 存在，尝试取对应角色
            if self.chat_id:
                chat = await sync_to_async(ChatRecord.objects.get)(id=int(self.chat_id))
                if chat.character:
                    self.character = await sync_to_async(Character.objects.get)(
                        id=chat.character.id
                    )
                    await self.send(text_data=json.dumps({
                        "sender": self.character.name,
                        "message": f"你好，我是 {self.character.name}，{self.character.description}"
                    }))
                    return

            # 默认使用助手
            self.character = await sync_to_async(Character.objects.get)(name="助手")
            await self.send(text_data=json.dumps({
                "sender": "助手",
                "message": "你好，我可以为你做些什么？"
            }))
        except Exception as e:
            print(f"连接错误: {e}")
            await self.send(text_data=json.dumps({
                "sender": "系统",
                "message": "连接时发生错误，请重试"
            }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("message", "")

        # 调用 AI
        reply = await sync_to_async(self.ask_ai)(user_message)

        sender = self.character.name if self.character else "助手"

        await self.send(text_data=json.dumps({
            "sender": sender,
            "message": reply
        }))

    def ask_ai(self, user_message: str) -> str:
        from .models import ChatRecord, Character

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            # system 提示
            system_content = (
                f"你现在要完全扮演 {self.character.name}。"
                f"角色设定：{self.character.description}。"
                f"请始终保持 {self.character.name} 的语气和身份来回答。"
            )

            # 取历史消息（保持 role + content 结构）
            history_query = ChatRecord.objects.filter(
                id=self.chat_id
            ) if self.chat_id else ChatRecord.objects.none()

            if hasattr(self.scope, "user") and getattr(self.scope["user"], "id", None):
                history_query = history_query.filter(user_id=self.scope["user"].id)

            if self.character:
                history_query = history_query.filter(character=self.character)

            history = list(history_query.order_by("created_at")[:10])

            # 构建消息列表
            messages = [{"role": "system", "content": system_content}]

            for record in history:
                try:
                    content = json.loads(record.content) if isinstance(record.content, str) else record.content
                    if isinstance(content, list):
                        for msg in content:
                            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                                messages.append(msg)
                    elif isinstance(content, dict):
                        if "role" in content and "content" in content:
                            messages.append(content)
                except Exception as parse_err:
                    print(f"历史消息解析失败: {parse_err}")
                    continue

            # 当前用户消息
            messages.append({"role": "user", "content": user_message.strip()})

            payload = {
                "model": "deepseek-v3",
                "messages": messages,
                "temperature": float(getattr(self.character, "temperature", 0.7)),
                "top_p": float(getattr(self.character, "top_p", 0.9)),
                "max_tokens": 1000
            }

            # 请求 API
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("choices"):
                raise ValueError("Invalid API response format")

            # 兼容不同格式
            reply = None
            if "message" in data["choices"][0]:
                reply = data["choices"][0]["message"]["content"]
            elif "text" in data["choices"][0]:
                reply = data["choices"][0]["text"]

            if not reply:
                raise ValueError("API response missing content")

            # 保存对话（严格 role/content 格式）
            try:
                record_data = {
                    "title": f"与{self.character.name}的对话" if self.character else "普通对话",
                    "content": [
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": reply}
                    ]
                }
                if hasattr(self.scope, "user") and getattr(self.scope["user"], "id", None):
                    record_data["user_id"] = self.scope["user"].id
                if self.character:
                    record_data["character"] = self.character

                ChatRecord.objects.create(**record_data)
            except Exception as db_error:
                print(f"数据库保存失败: {db_error}")

            return reply

        except Exception as e:
            return f"[错误] AI 接口调用失败: {e}"
