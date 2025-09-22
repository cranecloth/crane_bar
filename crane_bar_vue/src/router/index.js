import { createRouter, createWebHistory } from "vue-router";
import Chat from "../views/chat.vue";

const routes = [
  { path: "/", component: Chat }
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
