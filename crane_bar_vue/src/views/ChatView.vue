<template>
  <div class="chat-view">
    <!-- 左侧聊天列表 -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <h3>聊天记录</h3>
        <button @click="showNewChatDialog = true" class="new-chat-btn">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
          </svg>
        </button>
      </div>

      <div class="chat-list">
        <div
          v-for="chat in chatStore.chats"
          :key="chat.id"
          :class="[
            'chat-item',
            { active: chatStore.currentChatId === chat.id },
          ]"
          @click="selectChat(chat.id)"
        >
          <div class="chat-title">{{ chat.title }}</div>
          <div class="chat-time">{{ formatDate(chat.updated_at) }}</div>
          <button
            @click.stop="deleteChat(1, chat.id)"
            class="delete-chat-btn"
            title="删除聊天"
          >
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path
                fill="currentColor"
                d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧聊天主界面 -->
    <div class="chat-main">
      <div v-if="chatStore.currentChatId" class="chat-container">
        <div class="chat-header">
          <h2>{{ currentChatTitle }}</h2>
          <div class="typing-indicator" v-if="isTyping">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>

        <div class="messages-container" ref="messagesContainer">
          <transition-group name="message" tag="div">
            <div
              v-for="(msg, index) in chatStore.messages"
              :key="index"
              :class="[
                'message-bubble',
                msg.sender === '我' ? 'sent' : 'received',
              ]"
            >
              <div class="message-content">{{ msg.message }}</div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </transition-group>
        </div>

        <div class="input-area">
          <div class="input-wrapper">
            <input
              v-model="input"
              @keyup.enter="sendMessage"
              placeholder="输入消息..."
              @focus="scrollToBottom"
            />
            <button @click="sendMessage" :disabled="!input.trim()">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path
                  fill="currentColor"
                  d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-chat">
        <p>选择或创建一个新的聊天</p>
        <button @click="showNewChatDialog = true" class="new-chat-btn">
          新建聊天
        </button>
      </div>
    </div>

    <!-- 新建聊天对话框 -->
    <div v-if="showNewChatDialog" class="dialog-overlay">
      <div class="new-chat-dialog">
        <h3>新建聊天</h3>
        <div class="dialog-section">
          <label>聊天标题</label>
          <input v-model="newChatTitle" placeholder="输入聊天标题" />
        </div>

        <div class="dialog-section">
          <label>选择角色</label>
          <select v-model="selectedCharacterId" class="character-select">
            <option
              v-for="char in presetCharacters"
              :key="char.id"
              :value="char.id"
            >
              {{ char.character_name }}
            </option>
            <option value="custom">自定义角色</option>
          </select>
        </div>

        <div v-if="selectedCharacterId === 'custom'" class="dialog-section">
          <label>角色名称</label>
          <input v-model="customCharacter.name" placeholder="角色名称" />

          <label>角色描述</label>
          <textarea
            v-model="customCharacter.description"
            placeholder="角色背景描述"
          /><br />
          <label>角色开场白</label>
          <textarea
            v-model="customCharacter.greeting"
            placeholder="角色开场白"
          />

          <div class="param-grid">
            <div>
              <label>Temperature</label>
              <span>{{ customCharacter.temperature }}</span>

              <input
                type="range"
                v-model="customCharacter.temperature"
                min="0"
                max="2"
                step="0.1"
              />
            </div>
            <div>
              <label>Top P</label>
              <span>{{ customCharacter.top_p }}</span>

              <input
                type="range"
                v-model="customCharacter.top_p"
                min="0"
                max="1"
                step="0.05"
              />
            </div>
            <div>
              <label>Top K</label><span>{{ customCharacter.top_k }}</span>
              <input
                type="range"
                v-model="customCharacter.top_k"
                min="1"
                max="100"
                step="1"
              />
            </div>
          </div>
        </div>

        <div class="dialog-actions">
          <button @click="showNewChatDialog = false">取消</button>
          <button @click="createNewChat" :disabled="!newChatTitle.trim()">
            创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from "vue";
import { useChatStore } from "@/stores/chat";

const chatStore = useChatStore();
const input = ref("");
const isTyping = ref(false);
const messagesContainer = ref(null);
const showNewChatDialog = ref(false);
const newChatTitle = ref("");
const selectedCharacterId = ref("harry");
const showCharacterManager = ref(false);

// 预定义角色
const presetCharacters = ref([
  {
    id: "harry",
    character_name: "哈利波特",
    description: "霍格沃茨的学生，擅长魔法和魁地奇",
    greeting: "",
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
  },
  {
    id: "socrates",
    character_name: "苏格拉底",
    description: "古希腊哲学家，以提问和对话著称",
    greeting: "",
    temperature: 0.5,
    top_p: 0.8,
    top_k: 50,
  },
]);

// 自定义角色
const customCharacter = ref({
  id: "custom",
  character_name: "",
  description: "",
  greeting: "",
  temperature: 0.7,
  top_p: 0.9,
  top_k: 40,
});
let socket = null;

// 计算当前聊天标题
const currentChatTitle = computed(() => {
  const chat = chatStore.chats.find((c) => c.id === chatStore.currentChatId);
  return chat ? chat.title : "新聊天";
});

// 选择聊天
async function selectChat(chatId) {
  // 关闭现有连接
  if (socket) {
    socket.close();
    socket = null;
  }

  chatStore.currentChatId = chatId;
  await chatStore.loadMessages(1, chatId);

  // 使用chat_id建立新的WebSocket连接
  setupWebSocket(chatId);
}

// 保存当前聊天
async function saveCurrentChat() {
  if (!chatStore.currentChatId) return;

  const chatData = {
    id: chatStore.currentChatId,
    user_id: 1,
    title: currentChatTitle.value,
    content: JSON.stringify(chatStore.messages),
  };

  await chatStore.saveChat(chatData);
  await chatStore.loadChats(1);
}

// 删除聊天
async function deleteChat(userId, chatId) {
  try {
    if (confirm("确定要删除这个聊天记录吗？")) {
      await chatStore.deleteChat(userId, chatId);
      await chatStore.loadChats(userId);
      if (chatStore.currentChatId === chatId) {
        chatStore.currentChatId = null;
      }
    }
  } catch (error) {
    console.error("删除聊天记录失败:", error);
    alert(`删除聊天记录失败: ${error.message || "未知错误"}`);
  }
}

// 创建新聊天
async function createNewChat() {
  if (!newChatTitle.value.trim()) return;

  // 获取角色配置
  let characterConfig = {};
  if (selectedCharacterId.value === "custom") {
    characterConfig = {
      id: "custom",
      character_name: customCharacter.value.name,
      description: customCharacter.value.description,
      temperature: customCharacter.value.temperature,
      greeting: customCharacter.value.greeting,
      top_p: customCharacter.value.top_p,
      top_k: customCharacter.value.top_k,
    };
  } else {
    characterConfig = presetCharacters.value.find(
      (c) => c.id === selectedCharacterId.value
    );
  }

  const plainCharacter = JSON.parse(JSON.stringify(characterConfig));
  const chatData = {
    user_id: 1,
    title: newChatTitle.value,
    content: JSON.stringify([]),
    character: plainCharacter,
  };
  try {
    const newChat = await chatStore.saveChat(chatData);

    if (!newChat || !newChat.id) {
      console.error("创建聊天失败，返回数据：", newChat);
      return;
    }

    chatStore.currentChatId = newChat.id;
    chatStore.messages = [];
    showNewChatDialog.value = false;
    newChatTitle.value = "";

    // 设置 WebSocket 连接
    setupWebSocket(newChat.id, characterConfig);

    // 重新加载聊天列表
    await chatStore.loadChats(1);
  } catch (err) {
    console.error("创建新聊天失败:", err);
  }
}

function setupWebSocket(chatId) {
  if (socket) socket.close();

  const character = selectedCharacterId.value;
  const url = chatId
    ? `ws://localhost:8000/ws/chat/${chatId}/?character=${encodeURIComponent(
        character
      )}`
    : `ws://localhost:8000/ws/chat/?character=${encodeURIComponent(character)}`;
  socket = new WebSocket(url);
  socket.onmessage = async (event) => {
    isTyping.value = true;
    setTimeout(async () => {
      const data = JSON.parse(event.data);
      data.timestamp = new Date();
      chatStore.messages.push(data);
      isTyping.value = false;
      scrollToBottom();
      // 接收消息后也自动保存聊天记录
      await saveCurrentChat();
    }, 1000);
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
    alert("连接聊天服务器失败，请稍后重试");
  };
}

onMounted(async () => {
  try {
    await chatStore.loadChats(1);
  } catch (error) {
    console.error("加载聊天记录失败:", error);
  }
});

onBeforeUnmount(() => {
  if (socket) socket.close();
});

async function sendMessage() {
  if (input.value.trim()) {
    const msg = {
      sender: "我",
      message: input.value,
      timestamp: new Date(),
      character: selectedCharacterId.value,
    };
    chatStore.messages.push(msg);
    socket.send(
      JSON.stringify({
        message: input.value,
        character: selectedCharacterId.value,
      })
    );
    input.value = "";
    scrollToBottom();

    // 自动保存当前聊天记录
    await saveCurrentChat();
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

function formatTime(date) {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  if (!(dateObj instanceof Date) || isNaN(dateObj)) {
    return "";
  }
  return dateObj.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDate(dateStr) {
  const date = new Date(dateStr);
  return (
    date.toLocaleDateString() +
    " " +
    date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })
  );
}
</script>

<style scoped>
/* 粒子背景容器 */
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  opacity: 0.2;
}

.chat-view {
  position: relative;
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.chat-sidebar {
  width: 300px;
  background-color: rgba(30, 30, 50, 0.9);
  border-right: 1px solid var(--secondary-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid var(--secondary-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.new-chat-btn {
  background: var(--primary-color);
  color: #111;
  border: none;
  border-radius: 4px;
  padding: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.chat-item {
  padding: 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.05);
  position: relative;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.chat-item.active {
  background-color: var(--secondary-color);
}

.chat-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.chat-time {
  font-size: 0.75rem;
  opacity: 0.7;
}

.delete-chat-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 0.25rem;
}

.delete-chat-btn:hover {
  color: #ff6b6b;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

/* 聊天容器样式 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  margin: 1rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  scroll-behavior: smooth;
}

/* 消息气泡样式 */
.message-bubble {
  max-width: 80%;
  margin-bottom: 1rem;
  position: relative;
  transition: all 0.3s ease;
  transform-origin: bottom;
}

.message-bubble.sent {
  align-self: flex-end;
  background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
  color: white;
  border-radius: 18px 18px 0 18px;
  padding: 12px 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.message-bubble.received {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 18px 18px 18px 0;
  padding: 12px 16px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
}

.message-content {
  font-size: 1rem;
  line-height: 1.5;
  word-break: break-word;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 4px;
  text-align: right;
}

/* 消息动画 */
.message-enter-active,
.message-leave-active {
  transition: all 0.5s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.save-chat-btn {
  margin-left: auto;
  background: var(--primary-color);
  color: #111;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 新建聊天对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.new-chat-dialog {
  background: rgba(20, 20, 40, 0.95);
  backdrop-filter: blur(14px);
  padding: 2rem;
  border-radius: 16px;
  width: 600px;
  max-width: 95%;
  max-height: 90vh;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6);
  color: #ffffff;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s ease;
  overflow-y: auto;
  overflow-x: hidden;
}

.new-chat-dialog h3 {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 600;
  text-align: center;
  color: #00b4db;
}

/* 标签统一风格 */
.new-chat-dialog label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ccc;
  margin-top: 0.5rem;
  display: block;
}

/* 输入框、文本框、选择框 */
.new-chat-dialog input,
.new-chat-dialog textarea {
  width: calc(100% - 4rem);
  padding: 0.75rem 1rem;
  margin: 0.25rem 1rem 0 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.new-chat-dialog select {
  width: calc(100% - 4rem);
  padding: 0.75rem 1rem;
  margin: 0.25rem 1rem 0 1rem;
  background: rgba(30, 30, 50, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  font-size: 1rem;
  transition: all 0.3s ease;
  appearance: none;
  -webkit-appearance: none;
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1rem;
}

.new-chat-dialog select option {
  background: rgba(30, 30, 50, 0.9);
  color: #fff;
}

.new-chat-dialog select:focus {
  outline: none;
  border-color: #00b4db;
  box-shadow: 0 0 0 2px rgba(0, 180, 219, 0.3);
  background: rgba(30, 30, 50, 0.9);
}

.new-chat-dialog input:focus,
.new-chat-dialog textarea:focus,
.new-chat-dialog select:focus {
  outline: none;
  border-color: #00b4db;
  box-shadow: 0 0 0 2px rgba(0, 180, 219, 0.3);
  background: rgba(255, 255, 255, 0.1);
}

/* 自定义角色参数网格 */
.param-grid {
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 0.5rem;
}

.param-grid div {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.param-grid label {
  font-size: 0.8rem;
  color: #aaa;
}

.param-grid input[type="range"] {
  width: 80%;
}

/* 文本区统一高度 */
.new-chat-dialog textarea {
  resize: vertical;
  min-height: 100px;
  max-height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
  word-wrap: break-word;
  white-space: pre-wrap;
  width: calc(100% - 4rem);
}

/* 按钮组 */
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.dialog-actions button {
  padding: 0.6rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 0.95rem;
}

.dialog-actions button:first-child {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
}

.dialog-actions button:first-child:hover {
  background: rgba(255, 255, 255, 0.12);
}

.dialog-actions button:last-child {
  background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
  border: none;
  color: #fff;
}

.dialog-actions button:last-child:hover {
  filter: brightness(1.1);
}

/* 响应式优化 */
@media (max-width: 500px) {
  .new-chat-dialog {
    width: 90%;
    padding: 1.5rem;
  }

  .param-grid {
    grid-template-columns: 1fr;
  }
}

/* 输入区域样式 */
.input-area {
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(5px);
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.input-wrapper input {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 24px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-wrapper input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 2px rgba(0, 180, 219, 0.3);
}

.input-wrapper button {
  background: linear-gradient(135deg, #00b4db 0%, #0083b0 100%);
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.input-wrapper button:hover {
  transform: scale(1.05);
}

.input-wrapper button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
