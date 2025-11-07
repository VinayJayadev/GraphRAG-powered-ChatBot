import { create } from 'zustand';
import { ChatState, Message, Conversation, ConversationListItem } from '@/types/chat';
import { api } from '@/services/api';

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  conversations: [],
  currentConversationId: null,
  isLoading: false,
  conversationsLoading: false,
  error: null,

  addMessage: (message: Message) =>
    set((state) => ({
      messages: [...state.messages, { ...message, timestamp: message.timestamp || new Date().toISOString() }],
    })),

  setLoading: (loading: boolean) => set({ isLoading: loading }),

  setError: (error: string | null) => set({ error }),

  clearMessages: () => set({ messages: [], error: null, currentConversationId: null }),

  loadConversations: async () => {
    set({ conversationsLoading: true, error: null });
    try {
      const conversations = await api.conversations.list();
      set({ conversations, conversationsLoading: false });
    } catch (error: any) {
      console.error('Failed to load conversations:', error);
      // If it's a 503 (service unavailable) or database error, don't show error
      // Just return empty list - database might not be set up
      if (error?.response?.status === 503 || error?.response?.status === 500) {
        console.log('Database not available - continuing without chat history');
        set({ conversations: [], conversationsLoading: false, error: null });
      } else {
        set({ conversationsLoading: false, error: 'Failed to load conversations' });
      }
    }
  },

  createConversation: async (title: string) => {
    try {
      const conversation = await api.conversations.create(title);
      await get().loadConversations();
      return conversation;
    } catch (error) {
      console.error('Failed to create conversation:', error);
      throw error;
    }
  },

  selectConversation: async (id: string) => {
    set({ currentConversationId: id });
    await get().loadConversationMessages(id);
  },

  deleteConversation: async (id: string) => {
    try {
      await api.conversations.delete(id);
      if (get().currentConversationId === id) {
        set({ messages: [], currentConversationId: null });
      }
      await get().loadConversations();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      throw error;
    }
  },

  updateConversationTitle: async (id: string, title: string) => {
    try {
      await api.conversations.update(id, title);
      await get().loadConversations();
    } catch (error) {
      console.error('Failed to update conversation:', error);
      throw error;
    }
  },

  loadConversationMessages: async (id: string) => {
    try {
      const conversation = await api.conversations.get(id);
      const messages: Message[] = conversation.messages.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.created_at,
        metadata: msg.metadata,
      }));
      set({ messages, currentConversationId: id });
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
      set({ error: 'Failed to load conversation' });
    }
  },
}));
