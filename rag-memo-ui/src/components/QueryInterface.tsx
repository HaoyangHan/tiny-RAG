'use client';

import { useState } from 'react';
import { MagnifyingGlassIcon, SparklesIcon } from '@heroicons/react/24/outline';

interface QueryInterfaceProps {
  onQuery: (query: string) => void;
  isLoading: boolean;
  disabled: boolean;
}

const EXAMPLE_QUERIES = [
  "What is the main topic of the uploaded documents?",
  "Summarize the key points from the documents",
  "What are the most important findings?",
  "Can you explain the methodology used?"
];

export function QueryInterface({ onQuery, isLoading, disabled }: QueryInterfaceProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled && !isLoading) {
      onQuery(query.trim());
      setQuery('');
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    if (!disabled && !isLoading) {
      setQuery(exampleQuery);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Ask Questions</h2>
      
      {/* Query Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={disabled ? "Upload documents first to start asking questions..." : "Ask a question about your documents..."}
            disabled={disabled || isLoading}
            rows={4}
            className={`w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none ${
              disabled ? 'bg-gray-100 text-gray-500' : 'bg-white'
            }`}
          />
          <div className="absolute bottom-3 right-3">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
        </div>
        
        <button
          type="submit"
          disabled={disabled || isLoading || !query.trim()}
          className={`w-full flex items-center justify-center px-4 py-3 rounded-lg font-medium transition-colors ${
            disabled || isLoading || !query.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Processing...
            </>
          ) : (
            <>
              <SparklesIcon className="h-4 w-4 mr-2" />
              Ask Question
            </>
          )}
        </button>
      </form>

      {/* Example Queries */}
      {!disabled && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Example Questions:</h3>
          <div className="grid grid-cols-1 gap-2">
            {EXAMPLE_QUERIES.map((exampleQuery, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(exampleQuery)}
                disabled={isLoading}
                className="text-left p-3 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                &ldquo;{exampleQuery}&rdquo;
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Status */}
      {disabled && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-800">
                Please upload at least one document before asking questions.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 