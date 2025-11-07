"use client";

import React, { useState } from 'react';
import { useChatStore } from '@/store/chatStore';
import { ConversationListItem } from '@/types/chat';

interface ConversationListProps {
  conversations: ConversationListItem[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
}

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
}) => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      setDeletingId(id);
      try {
        await onDeleteConversation(id);
      } finally {
        setDeletingId(null);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (conversations.length === 0) {
    return (
      <div className="text-center py-8 px-4">
        <p className="text-gray-500 text-sm">No conversations yet</p>
        <p className="mt-2 text-xs text-gray-600">Start a new chat to begin</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {conversations.map((conv) => {
        const isActive = conv.id === currentConversationId;
        const isHovered = hoveredId === conv.id;
        const isDeleting = deletingId === conv.id;

        return (
          <div
            key={conv.id}
            className={`relative group cursor-pointer rounded-md transition-all duration-150 ${
              isActive
                ? 'bg-gray-800'
                : 'hover:bg-gray-800/50'
            }`}
            onMouseEnter={() => setHoveredId(conv.id)}
            onMouseLeave={() => setHoveredId(null)}
            onClick={() => onSelectConversation(conv.id)}
          >
            <div className="px-3 py-2.5">
              <div className="flex items-center justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <svg
                      className="w-4 h-4 text-gray-500 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                      />
                    </svg>
                    <h3
                      className={`text-sm truncate ${
                        isActive ? 'text-white' : 'text-gray-300'
                      }`}
                      title={conv.title}
                    >
                      {conv.title}
                    </h3>
                  </div>
                </div>

                {(isHovered || isActive) && (
                  <button
                    onClick={(e) => handleDelete(e, conv.id)}
                    disabled={isDeleting}
                    className={`flex-shrink-0 p-1 rounded hover:bg-gray-700 text-gray-400 hover:text-gray-200 transition-colors ${
                      isDeleting ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    title="Delete conversation"
                  >
                    {isDeleting ? (
                      <svg
                        className="w-3.5 h-3.5 animate-spin"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                    ) : (
                      <svg
                        className="w-3.5 h-3.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

