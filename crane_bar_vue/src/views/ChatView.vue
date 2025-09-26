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
          <button
            @click.stop="openEditCharacterDialog(1, chat.id)"
            class="edit-character-btn"
            title="修改角色"
          >
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path
                fill="currentColor"
                d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
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
          <div class="chat-title-wrapper">
            <h2>{{ currentChatTitle }}</h2>
            <span class="character-name">{{ character_name }}</span>
          </div>
          <div class="voice-wrapper">
            <span class="voice-label">音色选择</span>
            <select id="voiceSelect" v-model="selectedVoice">
              <option
                v-for="voice in voices"
                :key="voice.voice_type"
                :value="voice.voice_type"
              >
                {{ voice.voice_name }}
              </option>
            </select>
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
              <button
                v-if="msg.sender !== '我'"
                class="tts-btn"
                @click="playTTS(msg.message)"
              >
                🔊
              </button>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
            <div v-if="isTyping" class="typing-indicator">AI 正在输入中...</div>
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
            <button @click="toggleRecording">
              {{ isRecording ? "🛑" : "▶" }}
            </button>
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
          <input
            v-model="customCharacter.character_name"
            placeholder="角色名称"
          />

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
        <div v-if="selectedCharacterId === 'custom'" class="import-wrapper">
          <label>导入角色</label>
          <div class="import-box">
            <input
              type="file"
              accept="application/json"
              @change="importCharacterJson"
              class="import-section"
            />
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

  <!-- 修改角色对话框 -->
  <div v-if="showEditCharacterDialog" class="dialog-overlay">
    <div class="new-chat-dialog">
      <h3>修改角色设定</h3>
      <div class="dialog-section">
        <label>角色名称</label>
        <input
          v-model="editingCharacter.character_name"
          placeholder="角色名称"
        />
      </div>

      <div class="dialog-section">
        <label>角色描述</label>
        <textarea
          v-model="editingCharacter.character_description"
          placeholder="角色背景描述"
        />
      </div>

      <div class="param-grid">
        <div>
          <label>Temperature</label>
          <span>{{ editingCharacter.temperature }}</span>
          <input
            type="range"
            v-model="editingCharacter.temperature"
            min="0"
            max="2"
            step="0.1"
          />
        </div>
        <div>
          <label>Top P</label>
          <span>{{ editingCharacter.top_p }}</span>
          <input
            type="range"
            v-model="editingCharacter.top_p"
            min="0"
            max="1"
            step="0.05"
          />
        </div>
        <div>
          <label>Top K</label>
          <span>{{ editingCharacter.top_k }}</span>
          <input
            type="range"
            v-model="editingCharacter.top_k"
            min="1"
            max="100"
            step="1"
          />
        </div>
      </div>

      <div class="dialog-actions">
        <button @click="downloadCharacter">导出角色</button>
        <button @click="showEditCharacterDialog = false">取消</button>
        <button @click="updateCharacter">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from "vue";
import { useChatStore } from "@/stores/chat";

const chatStore = useChatStore();
const input = ref("");
const messagesContainer = ref(null);
const showNewChatDialog = ref(false);
const newChatTitle = ref("");
const selectedCharacterId = ref("harry");
const voices = ref([]);
const selectedVoice = ref(null);
let character_name = "";
const isRecording = ref(false);
let recognition = null;

const isTyping = computed(() => {
  const messages = chatStore.messages;
  if (!messages.length) return false;

  const lastMsg = messages[messages.length - 1];
  return lastMsg.sender === "我";
});

// 预定义角色
const presetCharacters = ref([
  {
    id: "harry",
    character_name: "哈利波特",
    description: "霍格沃茨的学生，擅长魔法和魁地奇",
    greeting:
      "嗨，我是哈利·波特。嗯……是的，就是那个额头上有闪电疤痕的家伙。最近霍格沃茨可不太平，总觉得有什么黑暗的气息在靠近。你愿意和我一起去禁林探险，或者偷偷去找一找那本神秘的魔法书吗？",
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40,
  },
  {
    id: "socrates",
    character_name: "苏格拉底",
    description: "古希腊哲学家，以提问和对话著称",
    greeting:
      "你好，我是苏格拉底。或许我并没有答案，但我会以提问来与你一同寻找真理。告诉我，朋友，你认为“幸福”的本质是什么呢？是财富、荣誉，还是灵魂的安宁？我很期待与你展开一场思想的对话。",
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

const showEditCharacterDialog = ref(false);
const editingCharacter = ref({
  id: "",
  character_name: "",
  character_description: "",
  greeting: "",
  temperature: 0.7,
  top_p: 0.9,
  top_k: 40,
  user_id: 0,
});
let socket = null;

// 计算当前聊天标题
const currentChatTitle = computed(() => {
  const chat = chatStore.chats.find((c) => c.id === chatStore.currentChatId);
  return chat ? chat.title : "新聊天";
});

// 选择聊天
function debounce(fn, delay = 300) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

async function _selectChat(chatId) {
  if (socket) {
    socket.close();
    socket = null;
  }

  chatStore.currentChatId = chatId;
  await chatStore.loadMessages(1, chatId);
  character_name = chatStore.character_name;
  getVoices();
  setupWebSocket(chatId);
}

const selectChat = debounce(_selectChat, 250);

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
// 修改角色设定
async function openEditCharacterDialog(userid, chatid) {
  await chatStore.loadMessages(userid, chatid);
  editingCharacter.value.character_name =
    chatStore.character_data.character_name;
  editingCharacter.value.character_description =
    chatStore.character_data.character_description;
  editingCharacter.value.temperature = chatStore.character_data.temperature;
  editingCharacter.value.top_p = chatStore.character_data.top_p;
  editingCharacter.value.top_k = chatStore.character_data.top_k;
  editingCharacter.value.greeting = chatStore.character_data.greeting;
  editingCharacter.value.id = chatStore.character_data.chat_id;
  editingCharacter.value.user_id = chatStore.character_data.user_id;
  console.log(editingCharacter.value);
  showEditCharacterDialog.value = true;
}

async function updateCharacter() {
  try {
    const response = await fetch(
      `http://localhost:8000/api/chat/${editingCharacter.value.user_id}/${editingCharacter.value.id}/`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(editingCharacter.value),
      }
    );

    if (!response.ok) {
      throw new Error("更新角色失败");
    }

    showEditCharacterDialog.value = false;
    await chatStore.loadChats(1);
  } catch (error) {
    console.error("更新角色失败:", error);
    alert(`更新角色失败: ${error.message || "未知错误"}`);
  }
}

// 导出角色
function exportJSON(editingCharacter, filename = "data.json") {
  const jsonStr = JSON.stringify(editingCharacter, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function downloadCharacter() {
  exportJSON(
    editingCharacter.value,
    `${editingCharacter.value.character_name || "角色"}.json`
  );
}

// 导入角色
function importCharacterJson(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target.result);
      customCharacter.value = {
        id: "custom",
        character_name: json.character_name || "",
        description: json.character_description || "",
        greeting: json.greeting || "",
        temperature: json.temperature ?? 0.7,
        top_p: json.top_p ?? 0.9,
        top_k: json.top_k ?? 40,
      };

      console.log("更新后的 customCharacter:", customCharacter.value);
    } catch (err) {
      console.error("导入失败:", err);
    }
  };
  reader.readAsText(file);
}

// 创建新聊天
async function createNewChat() {
  if (!newChatTitle.value.trim()) return;

  // 获取角色配置
  let characterConfig = {};
  if (selectedCharacterId.value === "custom") {
    characterConfig = {
      id: "custom",
      character_name: customCharacter.value.character_name,
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
    await getVoices();
  } catch (err) {
    console.error("创建新聊天失败:", err);
  }
}

async function playTTS(text) {
  try {
    const selectedVoice = document.getElementById("voiceSelect").value;
    const response = await fetch("https://openai.qiniu.com/v1/voice/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization:
          "Bearer sk-e38a1abe42b2acffa190cd2469e5d6cf000b7dc5c197eaadf3ea5a53f8275a49",
      },
      body: JSON.stringify({
        audio: {
          voice_type: selectedVoice,
          encoding: "mp3",
          speed_ratio: 1.0,
        },
        request: {
          text: text,
        },
      }),
    });

    const data = await response.json();
    if (
      data &&
      data.data &&
      typeof data.data === "string" &&
      data.data !== "data"
    ) {
      const audio = new Audio("data:audio/mp3;base64," + data.data);
      audio.play();
    } else if (data && data.addition && data.addition.url) {
      const audio = new Audio(data.addition.url);
      audio.play();
    } else {
      console.warn("TTS API 返回占位数据或格式异常:", data);
      alert("语音合成尚未完成或接口格式已更新，请使用音频 URL 播放");
    }
  } catch (error) {
    console.error("TTS 错误:", error);
    alert("语音合成失败，请检查控制台");
  }
}

async function getVoices() {
  try {
    const response = await fetch("https://openai.qiniu.com/v1/voice/list", {
      method: "GET",
      headers: {
        Authorization:
          "Bearer sk-e38a1abe42b2acffa190cd2469e5d6cf000b7dc5c197eaadf3ea5a53f8275a49",
      },
    });
    const data = await response.json();
    voices.value = data;
    if (data.length > 0) selectedVoice.value = data[0].voice_type;
  } catch (err) {
    console.error("获取音色失败:", err);
  }
}

async function toggleRecording() {
  if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
    alert("浏览器不支持语音识别，请使用 Chrome 或 Edge");
    return;
  }

  if (isRecording.value) {
    // 停止识别
    recognition.stop();
    isRecording.value = false;
  } else {
    try {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      recognition.lang = "zh-CN"; // 中文识别
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        isRecording.value = true;
        console.log("语音识别开始...");
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log("识别结果:", transcript);
        input.value = transcript;
      };

      recognition.onerror = (event) => {
        console.error("识别错误:", event.error);
        alert("语音识别出错: " + event.error);
      };

      recognition.onend = () => {
        isRecording.value = false;
        console.log("语音识别结束");
      };

      recognition.start();
    } catch (err) {
      console.error("语音识别失败:", err);
      alert("语音识别失败");
    }
  }
}

function setupWebSocket(chatId) {
  if (socket) socket.close();

  const character = selectedCharacterId.value;
  const url = `ws://localhost:8000/ws/chat/${chatId}/?character=${encodeURIComponent(
    character
  )}`;
  socket = new WebSocket(url);

  socket.onmessage = async (event) => {
    setTimeout(async () => {
      const data = JSON.parse(event.data);
      data.timestamp = new Date();
      chatStore.messages.push(data);
      scrollToBottom();
      await saveCurrentChat();
    }, 500);
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
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.character-name {
  font-size: 1rem;
  font-weight: 500;
}

.voice-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.voice-label {
  font-size: 0.9rem;
  color: #ccc;
  font-weight: 500;
}

#voiceSelect {
  padding: 0.5rem 1rem;
  border-radius: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.1); /* 半透明背景 */
  color: #fff; /* 字体颜色 */
  font-size: 1rem;
  transition: all 0.3s ease;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
}

#voiceSelect option {
  background: rgba(30, 30, 50, 0.9);
}

#voiceSelect:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 2px rgba(0, 180, 219, 0.3);
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

.edit-character-btn {
  position: absolute;
  top: 0.5rem;
  right: 1.75rem;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 0.25rem;
}

.edit-character-btn:hover {
  color: #4dabf7;
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
  max-height: 80vh;
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

.import-box {
  width: 50%;
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
.tts-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #00b4db;
  font-size: 1rem;
}
</style>
