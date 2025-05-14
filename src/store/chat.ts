import { defineStore } from "pinia";
import { useAuthStore } from "./auth"; 
import axios from "axios";
import apiConfig from '../utils/apiConfig';

interface ChatMessage {
  content: string;
  timestamp: string;
  sender_id?: number;
  receiver_id?: number;
  [key: string]: any;
}

interface ChatLastMessage {
  content: string;
  timestamp: string;
}

export const useChatStore = defineStore("chat", {
  state: () => ({
    isModalOpen: false,
    activeChatId: null as number | null,
    chatList: [] as any[],
    chatMessagesByChatId: {} as { [key: string]: ChatMessage[] },
    typingUser: null as string | null,
    unreadCounts: {} as { [key: string]: number },
    chatLastMessages: {} as { [key: string]: ChatLastMessage },
  }),
  actions: {
    toggleModal() { this.isModalOpen = !this.isModalOpen; },
    openChatModal() { this.isModalOpen = true; },
    closeChatModal() { this.isModalOpen = false; },
    clearActiveChat() { this.activeChatId = null; },
    setActiveChat(id: number) { this.activeChatId = id; },
    setChatList(chats: any[]) { this.chatList = chats; },
    setLastMessage(chatId: string | number, message: { content: string, timestamp: string }) {
      this.chatLastMessages[chatId.toString()] = {
        content: message.content,
        timestamp: message.timestamp,
      };
    },
    setMessages(chatId: string | number, msgs: ChatMessage[]) {
      this.chatMessagesByChatId[chatId.toString()] = msgs;
    },

    addMessage(chatId: string | number, msg: ChatMessage) {
      const id = chatId.toString();
      if (!this.chatMessagesByChatId[id]) {
        this.chatMessagesByChatId[id] = [];
      }
      this.chatMessagesByChatId[id].push(msg);
    },

    setTypingUser(user: string | null) { this.typingUser = user; },

    incrementUnread(chatId: string | number) {
      const id = chatId.toString();
      if (!this.unreadCounts[id]) {
        this.unreadCounts[id] = 1;
      } else {
        this.unreadCounts[id]++;
      }
    },

    resetUnread(chatId: string | number) {
      this.unreadCounts[chatId.toString()] = 0;
    },

    async fetchMessages(chatId: string | number) {
      try {
        const authStore = useAuthStore();
        const res = await axios.get(`${apiConfig.API_URL}/api/chats/${chatId}/messages/`, {
          headers: { Authorization: `Bearer ${authStore.token}` },
        });
        this.setMessages(chatId, res.data);
      } catch (err) {
        console.error("Failed to fetch messages", err);
      }
    },
  },
});
