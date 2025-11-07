import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '@/types/chat';
import { UserCircleIcon } from '@heroicons/react/24/solid';
import { GlobeAltIcon, BookOpenIcon } from '@heroicons/react/24/outline';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  // Get sources from metadata if available
  const sources = message.metadata?.sources || [];
  
  // Debug logging for sources
  if (!isUser && sources.length > 0) {
    console.log('📚 ChatMessage: Displaying sources:', {
      sourcesCount: sources.length,
      sources: sources,
    });
  } else if (!isUser && sources.length === 0) {
    console.log('⚠️ ChatMessage: No sources found in message:', {
      hasMetadata: !!message.metadata,
      metadata: message.metadata,
    });
  }

  return (
    <div className={`flex items-start gap-4 mb-6 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="w-8 h-8 bg-[#19c37d] rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-semibold">U</span>
          </div>
        ) : (
          <div className="w-8 h-8 bg-[#ab68ff] rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-semibold">AI</span>
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
        <div
          className={`inline-block rounded-2xl px-4 py-3 max-w-[85%] ${
            isUser
              ? 'bg-[#19c37d] text-white'
              : 'bg-white text-gray-900 border border-gray-200'
          }`}
        >
          <ReactMarkdown
            className="prose max-w-none prose-sm"
            components={{
              p: ({ children }) => <p className={`mb-3 last:mb-0 leading-7 whitespace-pre-wrap ${isUser ? 'text-white' : 'text-gray-900'}`}>{children}</p>,
              code: ({ children }) => (
                <code className={`rounded px-1.5 py-0.5 text-sm font-mono ${isUser ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  {children}
                </code>
              ),
              pre: ({ children }) => (
                <pre className={`rounded-lg p-4 overflow-x-auto my-4 ${isUser ? 'bg-white/20 text-white' : 'bg-gray-100'}`}>
                  {children}
                </pre>
              ),
              strong: ({ children }) => (
                <strong className={`font-semibold ${isUser ? 'text-white' : 'text-gray-900'}`}>
                  {children}
                </strong>
              ),
              ul: ({ children }) => (
                <ul className={`list-disc list-outside space-y-2 my-4 ml-6 ${isUser ? 'text-white' : 'text-gray-900'}`}>
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol className={`list-decimal list-outside space-y-2 my-4 ml-6 ${isUser ? 'text-white' : 'text-gray-900'}`}>
                  {children}
                </ol>
              ),
              li: ({ children }) => (
                <li className="leading-7">{children}</li>
              ),
              h1: ({ children }) => (
                <h1 className={`text-2xl font-bold mt-6 mb-4 ${isUser ? 'text-white' : 'text-gray-900'}`}>{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className={`text-xl font-bold mt-5 mb-3 ${isUser ? 'text-white' : 'text-gray-900'}`}>{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className={`text-lg font-bold mt-4 mb-2 ${isUser ? 'text-white' : 'text-gray-900'}`}>{children}</h3>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>

          {/* Sources */}
          {!isUser && sources.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-200">
              <div className="mb-2">
                <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                  Sources
                </span>
              </div>
              <div className="space-y-2">
                {sources.map((source, index) => {
                  if (source.type === 'knowledge_base') {
                    return (
                      <div
                        key={index}
                        className="bg-green-50 border border-green-200 rounded-lg p-3"
                        title={`Relevance score: ${source.score?.toFixed(3) || 'N/A'}`}
                      >
                        <div className="flex items-start gap-2">
                          <BookOpenIcon className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-xs font-semibold text-green-900">
                                {source.topic || source.filename || 'Knowledge Base'}
                              </span>
                              {source.category && (
                                <span className="text-xs text-green-700 bg-green-100 px-2 py-0.5 rounded">
                                  {source.category}
                                </span>
                              )}
                              {source.score !== undefined && source.score !== null && (
                                <span className="text-xs text-green-600">
                                  ({(source.score * 100).toFixed(1)}% match)
                                </span>
                              )}
                            </div>
                            {source.text_preview && (
                              <p className="text-xs text-green-800 mt-1 line-clamp-2">
                                {source.text_preview}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  } else if (source.type === 'web_search') {
                    return (
                      <div
                        key={index}
                        className="bg-blue-50 border border-blue-200 rounded-lg p-3"
                      >
                        <div className="flex items-start gap-2">
                          <GlobeAltIcon className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1">
                            <span className="text-xs font-semibold text-blue-900">
                              {source.source || 'Web Search'}
                            </span>
                            {source.query && (
                              <p className="text-xs text-blue-700 mt-1">
                                Query: "{source.query}"
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
