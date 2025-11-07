export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date | string;
  id?: string;
  metadata?: {
    sources?: Source[];
    rag_metadata?: Record<string, any>;
  };
}

export interface Source {
  type: 'knowledge_base' | 'web_search';
  topic?: string;
  category?: string;
  filename?: string;
  text_preview?: string;
  score?: number;
  source?: string;
  query?: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  user_id?: string;
  messages?: Message[];
}

export interface ConversationListItem {
  id: string;
  title: string;
  updated_at: string;
  preview?: string;
  message_count: number;
}

export interface ChatHistory {
  messages: Message[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  chat_history: { user: string; assistant?: string }[];
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  context: Array<{
    id: string;
    text: string;
    metadata: Record<string, any>;
  }>;
  metadata: {
    model: string;
    total_tokens: number;
    rag_documents_used?: number;
    web_search_used?: boolean;
  };
  sources?: Source[];
}

export interface ChatState {
  messages: Message[];
  conversations: ConversationListItem[];
  currentConversationId: string | null;
  isLoading: boolean;
  conversationsLoading: boolean;
  error: string | null;
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
  loadConversations: () => Promise<void>;
  createConversation: (title: string) => Promise<Conversation>;
  selectConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  updateConversationTitle: (id: string, title: string) => Promise<void>;
  loadConversationMessages: (id: string) => Promise<void>;
}
