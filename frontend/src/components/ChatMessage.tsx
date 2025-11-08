import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '@/types/chat';
import { UserCircleIcon } from '@heroicons/react/24/solid';
import { GlobeAltIcon, BookOpenIcon } from '@heroicons/react/24/outline';
import { SourceModal } from './SourceModal';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [selectedSource, setSelectedSource] = useState<{ filename: string; topic?: string } | null>(null);

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

  const handleSourceClick = (source: any) => {
    // Only allow clicking if it's a knowledge base source with a valid filename
    if (source.type === 'knowledge_base' && source.filename && source.filename !== 'Unknown' && source.has_file !== false) {
      setSelectedSource({
        filename: source.filename,
        topic: source.topic,
      });
    }
  };

  return (
    <div className={`group w-full text-gray-800 ${!isUser ? 'bg-gray-50' : 'bg-white'} border-b border-gray-100`}>
      <div className="flex gap-4 p-6 max-w-3xl mx-auto md:gap-6 md:py-8">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {isUser ? (
            <div className="w-8 h-8 rounded-sm bg-gray-800 flex items-center justify-center text-white text-sm font-semibold">
              U
            </div>
          ) : (
            <div className="w-8 h-8 rounded-sm bg-green-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className="flex-1 overflow-hidden">
          <div className="flex flex-col">
            <ReactMarkdown
              className="prose max-w-none text-base leading-7"
              components={{
                p: ({ children }) => <p className="mb-4 last:mb-0 whitespace-pre-wrap text-gray-800">{children}</p>,
                code: ({ children }) => (
                  <code className="rounded px-1.5 py-0.5 text-sm font-mono bg-black/10 text-gray-800">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="rounded-lg p-4 overflow-x-auto my-4 bg-black text-white">
                    {children}
                  </pre>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-900">
                    {children}
                  </strong>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-outside space-y-1 my-4 ml-6 text-gray-800">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-outside space-y-1 my-4 ml-6 text-gray-800">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="leading-7">{children}</li>
                ),
                h1: ({ children }) => (
                  <h1 className="text-2xl font-bold mt-6 mb-4 text-gray-900">{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-xl font-bold mt-5 mb-3 text-gray-900">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-lg font-bold mt-4 mb-2 text-gray-900">{children}</h3>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>

            {/* Sources */}
            {!isUser && sources.length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="mb-3">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {sources.filter(s => s.type === 'knowledge_base').length > 0 ? 'Primary Source' : 'Sources'}
                  </span>
                </div>
                <div className="space-y-2">
                  {sources.map((source, index) => {
                    // Highlight primary source (knowledge base) differently
                    const isPrimary = source.type === 'knowledge_base';
                    
                    if (source.type === 'knowledge_base') {
                      // Check if this source has a clickable file
                      const hasClickableFile = source.filename && source.filename !== 'Unknown' && source.has_file !== false;
                      
                      return (
                        <div
                          key={index}
                          className={`bg-blue-50 border-2 border-blue-200 rounded-md p-3 transition-colors ${
                            hasClickableFile 
                              ? 'hover:bg-blue-100 cursor-pointer' 
                              : 'cursor-default'
                          }`}
                          title={
                            hasClickableFile 
                              ? `Click to view source file - Relevance score: ${source.relevance_score || source.score?.toFixed(3) || 'N/A'}`
                              : `Primary source - Relevance score: ${source.relevance_score || source.score?.toFixed(3) || 'N/A'} (No file available)`
                          }
                          onClick={() => hasClickableFile && handleSourceClick(source)}
                        >
                          <div className="flex items-start gap-2">
                            <BookOpenIcon className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap mb-1">
                                <span className={`text-xs font-semibold text-blue-900 ${
                                  hasClickableFile ? 'hover:text-blue-700 underline' : ''
                                }`}>
                                  {source.topic || source.filename || 'Knowledge Base'}
                                </span>
                                <span className="text-xs font-medium text-blue-700 bg-blue-200 px-2 py-0.5 rounded">
                                  Primary Source
                                </span>
                                {source.category && (
                                  <span className="text-xs text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
                                    {source.category}
                                  </span>
                                )}
                                {(source.relevance_score || source.score) && (
                                  <span className="text-xs text-blue-600 font-medium">
                                    Match: {source.relevance_score || ((source.score || 0) * 100).toFixed(1) + '%'}
                                  </span>
                                )}
                                {hasClickableFile && (
                                  <span className="text-xs text-blue-600 italic">
                                    (Click to view file)
                                  </span>
                                )}
                              </div>
                              {source.text_preview && (
                                <p className="text-xs text-blue-800 mt-1 line-clamp-2">
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
                          className="bg-gray-100 border border-gray-200 rounded-md p-3 hover:bg-gray-200 transition-colors"
                        >
                          <div className="flex items-start gap-2">
                            <GlobeAltIcon className="h-4 w-4 text-gray-600 mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-medium text-gray-900">
                                  {source.source || 'Web Search'}
                                </span>
                                {source.note && (
                                  <span className="text-xs text-gray-600 bg-gray-200 px-2 py-0.5 rounded">
                                    {source.note}
                                  </span>
                                )}
                              </div>
                              {source.query && (
                                <p className="text-xs text-gray-700 mt-1">
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

      {/* Source Modal */}
      {selectedSource && (
        <SourceModal
          isOpen={!!selectedSource}
          onClose={() => setSelectedSource(null)}
          filename={selectedSource.filename}
          topic={selectedSource.topic}
        />
      )}
    </div>
  );
};
