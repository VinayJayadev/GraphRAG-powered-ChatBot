"use client";

import React, { useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { useChatStore } from '@/store/chatStore';
import { api } from '@/services/api';
import { Message } from '@/types/chat';

export const ChatWindow: React.FC = () => {
  const {
    messages,
    currentConversationId,
    isLoading,
    error,
    addMessage,
    setLoading,
    setError,
    loadConversations,
  } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Reload conversations after sending message to update the list
  useEffect(() => {
    if (!isLoading && currentConversationId) {
      loadConversations();
    }
  }, [isLoading, currentConversationId, loadConversations]);


  const handleSendMessage = async (content: string) => {
    try {
      // Add user message optimistically
      const userMessage: Message = {
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      addMessage(userMessage);
      setLoading(true);
      setError(null);

      // Prepare chat history for API (for backward compatibility)
      const chatHistory = messages
        .filter((msg) => msg.role === 'user' || msg.role === 'assistant')
        .reduce<Array<{ user: string; assistant?: string }>>((acc, msg, idx, arr) => {
          if (msg.role === 'user') {
            const assistantMsg = arr[idx + 1];
            acc.push({
              user: msg.content,
              assistant: assistantMsg && assistantMsg.role === 'assistant' ? assistantMsg.content : undefined,
            });
          }
          return acc;
        }, []);

      // Send message to API
      const response = await api.chat.sendMessage(
        content,
        currentConversationId || undefined,
        chatHistory
      );

      // Update conversation ID if this is a new conversation
      if (response.conversation_id && !currentConversationId) {
        useChatStore.getState().currentConversationId = response.conversation_id;
        await loadConversations();
      }

      // Add assistant message with sources
      console.log('📋 ChatWindow: Received response with sources:', {
        sourcesCount: response.sources?.length || 0,
        sources: response.sources,
        metadata: response.metadata,
      });
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        metadata: {
          sources: response.sources || [],
          rag_metadata: response.metadata,
        },
      };
      
      console.log('💬 ChatWindow: Created assistant message:', {
        hasMetadata: !!assistantMessage.metadata,
        sourcesCount: assistantMessage.metadata?.sources?.length || 0,
        sources: assistantMessage.metadata?.sources,
      });
      
      addMessage(assistantMessage);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'An error occurred while sending message'
      );
      // Remove the user message if there was an error
      // In a production app, you might want to mark it as failed instead
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 && !isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-2xl px-6">
              <h1 className="text-4xl font-semibold text-gray-800 mb-4">Graph RAG Assistant</h1>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-xl mx-auto mt-8">
                <button
                  onClick={() => handleSendMessage("What is machine learning?")}
                  className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="font-medium text-gray-900 mb-1">What is machine learning?</div>
                  <div className="text-sm text-gray-600">Learn about ML concepts</div>
                </button>
                <button
                  onClick={() => handleSendMessage("Explain blockchain technology")}
                  className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="font-medium text-gray-900 mb-1">Explain blockchain</div>
                  <div className="text-sm text-gray-600">Understand blockchain</div>
                </button>
                <button
                  onClick={() => handleSendMessage("What are the latest AI trends?")}
                  className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="font-medium text-gray-900 mb-1">Latest AI trends</div>
                  <div className="text-sm text-gray-600">Current AI developments</div>
                </button>
                <button
                  onClick={() => handleSendMessage("Tell me about data science")}
                  className="p-4 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="font-medium text-gray-900 mb-1">Data science basics</div>
                  <div className="text-sm text-gray-600">Introduction to data science</div>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto px-4 py-8">
            {messages.map((message, index) => (
              <ChatMessage key={message.id || index} message={message} />
            ))}
            
            {isLoading && (
              <div className="flex items-start gap-4 mb-6">
                <div className="w-8 h-8 bg-[#ab68ff] rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-xs font-semibold">AI</span>
                </div>
                <div className="flex items-center gap-1 pt-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            )}
            
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-3">
                  <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                  </svg>
                  <div>
                    <p className="font-medium text-red-800">Error occurred</p>
                    <p className="text-red-600 text-sm">{error}</p>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white">
        <div className="max-w-3xl mx-auto p-4">
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};
