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
    <div className="w-[260px] bg-slate-950 flex flex-col h-full text-gray-300 border-r border-gray-800">
      {/* New Chat Button */}
      <div className="p-3 border-b border-gray-800">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-3 px-3 py-2.5 text-sm text-white bg-transparent border border-gray-700 rounded-lg hover:bg-gray-800 transition-colors duration-150"
        >
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
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span>New chat</span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto px-2 pb-2">
        {conversationsLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-600 border-t-gray-400"></div>
          </div>
        ) : (
          <ConversationList
            conversations={conversations}
            currentConversationId={currentConversationId}
            onSelectConversation={handleSelectConversation}
            onDeleteConversation={handleDeleteConversation}
          />
        )}
      </div>

      {/* User Profile */}
      <div className="p-3 border-t border-gray-800">
        <div className="flex items-center gap-3 px-2 py-2 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer">
          <div className="w-7 h-7 bg-gray-700 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-medium">U</span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-white text-sm font-medium truncate">User</div>
            <div className="text-gray-500 text-xs truncate">Free Plan</div>
          </div>
        </div>
      </div>
    </div>
  );
};

