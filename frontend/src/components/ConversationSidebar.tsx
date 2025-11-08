"use client";

import React, { useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import { ConversationList } from './ConversationList';

export const ConversationSidebar: React.FC = () => {
  const {
    conversations,
    currentConversationId,
    conversationsLoading,
    loadConversations,
    selectConversation,
    deleteConversation,
    clearMessages,
  } = useChatStore();

  useEffect(() => {
    // Load conversations on mount, but don't show error if database is not available
    loadConversations().catch((err) => {
      // Silently fail - database might not be set up
      console.log('Conversations not available (database may not be configured)');
    });
  }, [loadConversations]);

  const handleNewChat = () => {
    clearMessages();
  };

  const handleSelectConversation = async (id: string) => {
    await selectConversation(id);
  };

  const handleDeleteConversation = async (id: string) => {
    await deleteConversation(id);
  };

  return (
    <div className="w-[280px] bg-gray-900 flex flex-col h-full text-gray-300 border-r border-gray-800 dark-scrollbar">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white">Chat History</h2>
        <p className="text-xs text-gray-400 mt-1">Your conversations</p>
      </div>

      {/* New Chat Button */}
      <div className="p-3 border-b border-gray-800">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors duration-150 font-medium shadow-sm"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span>New Chat</span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto">
        {conversationsLoading ? (
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-gray-600 border-t-green-500 mb-3"></div>
            <p className="text-xs text-gray-400">Loading conversations...</p>
          </div>
        ) : conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <svg
              className="w-12 h-12 text-gray-600 mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-sm text-gray-400 mb-1">No conversations yet</p>
            <p className="text-xs text-gray-500">Start a new chat to begin</p>
          </div>
        ) : (
          <div className="p-2">
            <ConversationList
              conversations={conversations}
              currentConversationId={currentConversationId}
              onSelectConversation={handleSelectConversation}
              onDeleteConversation={handleDeleteConversation}
            />
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-gray-800 bg-gray-800/50">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{conversations.length} conversation{conversations.length !== 1 ? 's' : ''}</span>
        </div>
      </div>
    </div>
  );
};

