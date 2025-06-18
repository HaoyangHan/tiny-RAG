'use client';

import { useState } from 'react';
import { DocumentUpload } from '@/components/DocumentUpload';
import { QueryInterface } from '@/components/QueryInterface';
import { ResultsDisplay } from '@/components/ResultsDisplay';

interface QueryResult {
  answer: string;
  sources: string[];
  confidence: number;
}

export default function RAGWorkflowPage() {
  const [documents, setDocuments] = useState<string[]>([]);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleDocumentUpload = (fileName: string) => {
    setDocuments(prev => [...prev, fileName]);
  };

  const handleQuery = async (query: string) => {
    setIsLoading(true);
    try {
      // Mock API call - replace with actual API
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, documents })
      });
      
      if (response.ok) {
        const result = await response.json();
        setQueryResult(result);
      } else {
        // Mock result for demo
        setQueryResult({
          answer: `Based on the uploaded documents, here's what I found about: "${query}". This is a demo response since the API is not yet fully connected.`,
          sources: documents.slice(0, 2),
          confidence: 0.85
        });
      }
    } catch (error) {
      console.error('Query failed:', error);
      setQueryResult({
        answer: 'Sorry, I encountered an error processing your query. Please try again.',
        sources: [],
        confidence: 0
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            TinyRAG Workflow
          </h1>
          <p className="text-lg text-gray-600">
            Upload documents, ask questions, and get intelligent answers
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Document Upload */}
          <div className="space-y-6">
            <DocumentUpload 
              onUpload={handleDocumentUpload}
              uploadedDocuments={documents}
            />
          </div>

          {/* Right Column - Query Interface */}
          <div className="space-y-6">
            <QueryInterface 
              onQuery={handleQuery}
              isLoading={isLoading}
              disabled={documents.length === 0}
            />
            
            {queryResult && (
              <ResultsDisplay result={queryResult} />
            )}
          </div>
        </div>

        {/* Status Bar */}
        <div className="mt-8 p-4 bg-white rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Documents: {documents.length}
              </span>
              <span className="text-sm text-gray-600">
                Status: {isLoading ? 'Processing...' : 'Ready'}
              </span>
            </div>
            <div className="text-xs text-gray-400">
              TinyRAG v0.1.0
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
