"use client";

import React, { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, SparklesIcon } from '@heroicons/react/24/solid';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const quickPrompts = [
    "What is machine learning?",
    "Tell me about AI developments",
    "Explain blockchain technology",
    "What are the latest trends?"
  ];

  return (
    <div className="relative">
      {/* Input Area */}
      <div className="relative flex items-end rounded-2xl border border-gray-300 bg-white shadow-sm focus-within:border-gray-400 focus-within:shadow-md transition-all">
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Message Graph RAG Assistant..."
            disabled={disabled}
            className="w-full resize-none bg-transparent text-gray-900 placeholder-gray-500 focus:outline-none min-h-[52px] max-h-32 py-3 px-4 text-base leading-6"
            rows={1}
            style={{ height: 'auto' }}
          />
        </div>
        
        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className={`flex-shrink-0 m-2 p-2 rounded-lg transition-all ${
            disabled || !message.trim()
              ? 'text-gray-400 cursor-not-allowed'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
          title="Send message"
        >
          {disabled ? (
            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};
