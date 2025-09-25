import { defineStore } from "pinia";
import { ref } from "vue";

export const useChatStore = defineStore("chat", () => {
  const currentChatId = ref(null);
  const chats = ref([]);
  const messages = ref([]);
  const isLoading = ref(false);
  const character_name = ref("");

  async function loadChats(userId) {
    try {
      isLoading.value = true;
      const response = await fetch(
        `http://localhost:8000/api/chat/list/?user_id=${userId}`
      );
      chats.value = await response.json();
    } finally {
      isLoading.value = false;
    }
  }

  async function saveChat(chatData) {
    try {
      isLoading.value = true;
      const method = chatData.id ? "PUT" : "POST";
      const url = chatData.id
        ? `http://localhost:8000/api/chat/${chatData.user_id}/${chatData.id}/`
        : "http://localhost:8000/api/chat/save/";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(chatData),
      });
      return await response.json();
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteChat(userId, chatId) {
    try {
      isLoading.value = true;
      await fetch(`http://localhost:8000/api/chat/${userId}/${chatId}/`, {
        method: "DELETE",
      });
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMessages(userId, chatId) {
    try {
      isLoading.value = true;
      const response = await fetch(
        `http://localhost:8000/api/chat/${userId}/${chatId}/`
      );
      if (!response.ok) {
        throw new Error("Failed to load messages");
      }
      const data = await response.json();
      character_name.value = data.character_name;
      messages.value = JSON.parse(data.content);
    } catch (error) {
      console.error("Error loading messages:", error);
      messages.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  return {
    currentChatId,
    chats,
    messages,
    isLoading,
    character_name,
    loadChats,
    saveChat,
    deleteChat,
    loadMessages,
  };
});
