import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const api = {
  // Chat
  chat: {
    sendMessage: async (message: string, conversationId?: string, chatHistory: any[] = []) => {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message,
        conversation_id: conversationId,
        chat_history: chatHistory,
      });
      return response.data;
    },
  },

  // Conversations
  conversations: {
    list: async () => {
      const response = await axios.get(`${API_BASE_URL}/conversations`);
      return response.data;
    },

    get: async (id: string) => {
      const response = await axios.get(`${API_BASE_URL}/conversations/${id}`);
      return response.data;
    },

    create: async (title: string) => {
      const response = await axios.post(`${API_BASE_URL}/conversations`, {
        title,
      });
      return response.data;
    },

    update: async (id: string, title: string) => {
      const response = await axios.put(`${API_BASE_URL}/conversations/${id}`, {
        title,
      });
      return response.data;
    },

    delete: async (id: string) => {
      await axios.delete(`${API_BASE_URL}/conversations/${id}`);
    },

    getMessages: async (id: string) => {
      const response = await axios.get(`${API_BASE_URL}/conversations/${id}/messages`);
      return response.data;
    },
  },
};

