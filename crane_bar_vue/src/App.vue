<script setup>
import { ref } from "vue";
import ChatView from "./views/ChatView.vue";
</script>

<template>
  <ChatView />
</template>

<style>
:root {
  --bg-color: #1a1a2e;
  --text-color: #e6e6e6;
  --primary-color: #4cc9f0;
  --secondary-color: #4361ee;
}

body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: var(--text-color);
  background-color: var(--bg-color);
}
</style>
