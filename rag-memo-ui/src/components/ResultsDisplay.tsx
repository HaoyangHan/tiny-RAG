'use client';

import { CheckCircleIcon, DocumentIcon } from '@heroicons/react/24/outline';

interface QueryResult {
  answer: string;
  sources: string[];
  confidence: number;
}

interface ResultsDisplayProps {
  result: QueryResult;
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <CheckCircleIcon className="h-5 w-5 text-green-600" />
        <h2 className="text-xl font-semibold text-gray-900">Answer</h2>
      </div>

      {/* Answer */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {result.answer}
          </p>
        </div>
      </div>

      {/* Confidence Score */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <span className="text-sm font-medium text-gray-700">Confidence Score:</span>
        <div className="flex items-center space-x-2">
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(result.confidence)}`}
          >
            {getConfidenceLabel(result.confidence)}
          </span>
          <span className="text-sm text-gray-600">
            {Math.round(result.confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Sources */}
      {result.sources.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-gray-900">Sources</h3>
          <div className="space-y-2">
            {result.sources.map((source, index) => (
              <div
                key={index}
                className="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-lg"
              >
                <DocumentIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                <span className="text-sm text-gray-700">{source}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metadata */}
      <div className="text-xs text-gray-500 border-t pt-4">
        <div className="flex items-center justify-between">
          <span>Generated at {new Date().toLocaleString()}</span>
          <span>Based on {result.sources.length} source(s)</span>
        </div>
      </div>
    </div>
  );
} 