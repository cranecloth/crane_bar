<template>
  <div class="chat">
    <h2>和 {{ roleName }} 聊天</h2>
    <div class="messages">
      <div v-for="(msg, index) in messages" :key="index">
        <b>{{ msg.sender }}:</b> {{ msg.message }}
      </div>
    </div>
    <input
      v-model="input"
      @keyup.enter="sendMessage"
      placeholder="输入消息..."
    />
    <button @click="sendMessage">发送</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";

const roleName = "哈利波特";
const messages = ref([]);
const input = ref("");
let socket = null;

onMounted(() => {
  socket = new WebSocket(
    `ws://localhost:8000/ws/chat/${encodeURIComponent(roleName)}/`
  );

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    messages.value.push(data);
  };
});

onBeforeUnmount(() => {
  if (socket) socket.close();
});

function sendMessage() {
  if (input.value.trim()) {
    const msg = { sender: "我", message: input.value };
    messages.value.push(msg);
    socket.send(JSON.stringify({ message: input.value }));
    input.value = "";
  }
}
</script>

<style>
.chat {
  max-width: 600px;
  margin: auto;
  font-family: sans-serif;
}
.messages {
  border: 1px solid #ccc;
  height: 300px;
  overflow-y: auto;
  padding: 8px;
  margin-bottom: 10px;
}
</style>
