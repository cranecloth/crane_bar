import { createRouter, createWebHistory } from "vue-router";
import ChatView from "../views/ChatView.vue";
import CharacterManager from "../views/CharacterManager.vue";

const routes = [
  { path: "/", component: ChatView },
  { path: "/characters", component: CharacterManager }
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
