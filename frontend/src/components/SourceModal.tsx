import React, { useEffect, useState, useCallback } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { api } from '@/services/api';

interface SourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  filename: string;
  topic?: string;
}

export const SourceModal: React.FC<SourceModalProps> = ({ isOpen, onClose, filename, topic }) => {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFileContent = useCallback(async () => {
    if (!filename) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await api.knowledgeBase.getFile(filename);
      setContent(response.content);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load file content');
      console.error('Error fetching file content:', err);
    } finally {
      setLoading(false);
    }
  }, [filename]);

  useEffect(() => {
    if (isOpen && filename) {
      fetchFileContent();
    } else if (!isOpen) {
      // Clear content when modal closes
      setContent('');
      setError(null);
    }
  }, [isOpen, filename, fetchFileContent]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-semibold text-gray-900 truncate">
              {topic || filename.replace('.txt', '').replace('_', ' ')}
            </h2>
            <p className="text-sm text-gray-500 mt-1">{filename}</p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Close modal"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
          {!loading && !error && content && (
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans leading-relaxed">
                {content}
              </pre>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end p-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

