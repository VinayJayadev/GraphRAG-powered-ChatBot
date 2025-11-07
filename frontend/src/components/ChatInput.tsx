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
      <div className="relative flex items-end rounded-3xl border border-gray-300 bg-white shadow-lg focus-within:shadow-xl transition-all">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Message ChatGPT..."
          disabled={disabled}
          className="w-full resize-none bg-transparent text-gray-900 placeholder-gray-400 focus:outline-none min-h-[52px] max-h-32 py-4 pl-5 pr-12 text-base leading-6"
          rows={1}
          style={{ height: 'auto' }}
        />

        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className={`absolute right-2 bottom-2 p-2 rounded-lg transition-all ${
            disabled || !message.trim()
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-gray-900 text-white hover:bg-gray-800'
          }`}
          title="Send message"
        >
          {disabled ? (
            <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          )}
        </button>
      </div>
      <p className="text-xs text-gray-500 text-center mt-3">
        ChatGPT can make mistakes. Check important info.
      </p>
    </div>
  );
};
