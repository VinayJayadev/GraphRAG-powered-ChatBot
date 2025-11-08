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

  return (
    <div className="space-y-1">
      {conversations.map((conv) => {
        const isActive = conv.id === currentConversationId;
        const isHovered = hoveredId === conv.id;
        const isDeleting = deletingId === conv.id;

        return (
          <div
            key={conv.id}
            className={`relative group cursor-pointer rounded-lg transition-all duration-150 ${
              isActive
                ? 'bg-green-600/20 border border-green-600/30'
                : 'hover:bg-gray-800/70 border border-transparent'
            }`}
            onMouseEnter={() => setHoveredId(conv.id)}
            onMouseLeave={() => setHoveredId(null)}
            onClick={() => onSelectConversation(conv.id)}
          >
            <div className="px-3 py-2.5">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-start gap-2.5">
                    <div className={`flex-shrink-0 mt-0.5 ${
                      isActive ? 'text-green-400' : 'text-gray-500'
                    }`}>
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
                          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                        />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3
                        className={`text-sm font-medium truncate mb-1 ${
                          isActive ? 'text-white' : 'text-gray-200'
                        }`}
                        title={conv.title}
                      >
                        {conv.title}
                      </h3>
                      {conv.preview && (
                        <p className="text-xs text-gray-400 line-clamp-2 mb-1">
                          {conv.preview}
                        </p>
                      )}
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500">
                          {formatDate(conv.updated_at)}
                        </span>
                        {conv.message_count > 0 && (
                          <>
                            <span className="text-gray-600">•</span>
                            <span className="text-xs text-gray-500">
                              {conv.message_count} message{conv.message_count !== 1 ? 's' : ''}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {(isHovered || isActive) && (
                  <button
                    onClick={(e) => handleDelete(e, conv.id)}
                    disabled={isDeleting}
                    className={`flex-shrink-0 p-1.5 rounded-md hover:bg-gray-700/50 text-gray-400 hover:text-red-400 transition-colors ${
                      isDeleting ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                    title="Delete conversation"
                  >
                    {isDeleting ? (
                      <svg
                        className="w-4 h-4 animate-spin"
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
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
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

