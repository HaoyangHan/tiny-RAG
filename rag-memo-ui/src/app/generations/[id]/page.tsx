'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ChevronLeftIcon,
  ClockIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  XCircleIcon,
  SparklesIcon,
  ChartBarIcon,
  LinkIcon,
  StarIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Generation, GenerationStatus, Document } from '@/types';

interface GenerationDetailsProps {
  params: { id: string };
}

export default function GenerationDetailsPage({ params }: GenerationDetailsProps) {
  const router = useRouter();
  const [copied, setCopied] = useState(false);

  // Mock generation data - replace with actual API call
  const mockGeneration: Generation = {
    id: params.id || '1',
    element_id: 'element-1',
    element_name: 'Customer Query Processor',
    project_id: 'project-1',
    status: GenerationStatus.COMPLETED,
    input_data: {
      customer_query: "What is your return policy?",
      context: "e-commerce platform",
      urgency: "medium"
    },
    output_text: `Based on your customer query about our return policy, here's a comprehensive response:

Our return policy allows customers to return items within 30 days of purchase for a full refund. Items must be in their original condition with tags attached. We provide prepaid return labels for your convenience.

For electronic items, we offer a 14-day return window. Custom or personalized items are generally not eligible for returns unless they arrive damaged.

To initiate a return, customers can:
1. Visit our returns portal online
2. Contact customer service at 1-800-RETURNS
3. Visit any of our physical store locations

We typically process refunds within 3-5 business days after receiving the returned item.`,
    model_used: 'gpt-4-turbo-preview',
    tokens_used: 1247,
    execution_time: 3420,
    cost: 0.0485,
    error_message: undefined,
    created_at: '2024-02-20T14:30:00Z',
    updated_at: '2024-02-20T14:30:03Z'
  };

  // Mock source documents
  const mockDocuments: Document[] = [
    {
      id: 'doc-1',
      user_id: 'user-1',
      project_id: 'project-1',
      filename: 'Return Policy Documentation',
      content_type: 'application/pdf',
      file_size: 156789,
      status: 'COMPLETED' as any,
      chunk_count: 12,
      metadata: { pages: 8, language: 'en' },
      created_at: '2024-02-15T10:00:00Z',
      updated_at: '2024-02-15T10:05:00Z',
      is_deleted: false
    },
    {
      id: 'doc-2',
      user_id: 'user-1',
      project_id: 'project-1',
      filename: 'Customer Service Guidelines',
      content_type: 'text/plain',
      file_size: 89234,
      status: 'COMPLETED' as any,
      chunk_count: 6,
      metadata: { sections: 15, version: '2.1' },
      created_at: '2024-02-18T16:20:00Z',
      updated_at: '2024-02-18T16:22:00Z',
      is_deleted: false
    }
  ];

  const handleCopyOutput = async () => {
    try {
      await navigator.clipboard.writeText(mockGeneration.output_text || '');
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const getStatusIcon = () => {
    switch (mockGeneration.status) {
      case GenerationStatus.COMPLETED:
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      case GenerationStatus.FAILED:
        return <XCircleIcon className="h-6 w-6 text-red-500" />;
      case GenerationStatus.PROCESSING:
        return (
          <div className="animate-spin h-6 w-6 border-2 border-blue-500 border-t-transparent rounded-full" />
        );
      default:
        return <ClockIcon className="h-6 w-6 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (mockGeneration.status) {
      case GenerationStatus.COMPLETED:
        return 'bg-green-100 text-green-800';
      case GenerationStatus.FAILED:
        return 'bg-red-100 text-red-800';
      case GenerationStatus.PROCESSING:
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <DashboardLayout title="Generation Details">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/generations')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to Generations
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Generation Header */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getStatusIcon()}
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Generation Details</h1>
                    <p className="text-gray-600">
                      From element: <span className="font-medium">{mockGeneration.element_name}</span>
                    </p>
                  </div>
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor()}`}>
                  {mockGeneration.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <ClockIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Execution Time</p>
                  <p className="text-lg font-semibold text-gray-900">{mockGeneration.execution_time}s</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <CpuChipIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Tokens Used</p>
                  <p className="text-lg font-semibold text-gray-900">{mockGeneration.tokens_used.toLocaleString()}</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <ChartBarIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Cost</p>
                  <p className="text-lg font-semibold text-gray-900">${mockGeneration.cost.toFixed(4)}</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <SparklesIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Model</p>
                  <p className="text-lg font-semibold text-gray-900">{mockGeneration.model_used}</p>
                </div>
              </div>
            </div>

            {/* Input Data */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Input Data</h2>
              <div className="space-y-4">
                {Object.entries(mockGeneration.input_data).map(([key, value]) => (
                  <div key={key}>
                    <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                      {key.replace('_', ' ')}
                    </label>
                    <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                        {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Generated Output */}
            {mockGeneration.status === GenerationStatus.COMPLETED && mockGeneration.output_text && (
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-medium text-gray-900">Generated Output</h2>
                  <button
                    onClick={handleCopyOutput}
                    className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                  <div className="prose prose-sm max-w-none">
                    <pre className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                      {mockGeneration.output_text}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {mockGeneration.status === GenerationStatus.FAILED && mockGeneration.error_message && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Error Details</h2>
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="flex">
                    <ExclamationCircleIcon className="h-5 w-5 text-red-400 mr-2 mt-0.5" />
                    <div className="text-sm text-red-700">
                      <p className="font-medium">Generation Failed</p>
                      <p className="mt-1">{mockGeneration.error_message}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Performance Metrics */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Token Breakdown</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Input Tokens</span>
                      <span className="font-medium">{Math.floor(mockGeneration.tokens_used * 0.6).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Output Tokens</span>
                      <span className="font-medium">{Math.floor(mockGeneration.tokens_used * 0.4).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm border-t pt-2">
                      <span className="text-gray-700 font-medium">Total Tokens</span>
                      <span className="font-semibold">{mockGeneration.tokens_used.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Cost Analysis</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Input Cost</span>
                      <span className="font-medium">${(mockGeneration.cost * 0.6).toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Output Cost</span>
                      <span className="font-medium">${(mockGeneration.cost * 0.4).toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between text-sm border-t pt-2">
                      <span className="text-gray-700 font-medium">Total Cost</span>
                      <span className="font-semibold">${mockGeneration.cost.toFixed(4)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Generation Info */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Generation Info</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-500">ID</p>
                  <p className="text-sm text-gray-900 font-mono">{mockGeneration.id}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Created</p>
                  <p className="text-sm text-gray-900">
                    {new Date(mockGeneration.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Element</p>
                  <button
                    onClick={() => router.push(`/elements/${mockGeneration.element_id}`)}
                    className="text-sm text-blue-600 hover:text-blue-500 flex items-center"
                  >
                    {mockGeneration.element_name}
                    <LinkIcon className="h-3 w-3 ml-1" />
                  </button>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Project</p>
                  <button
                    onClick={() => router.push(`/projects/${mockGeneration.project_id}`)}
                    className="text-sm text-blue-600 hover:text-blue-500 flex items-center"
                  >
                    View Project
                    <LinkIcon className="h-3 w-3 ml-1" />
                  </button>
                </div>
              </div>
            </div>

            {/* Source Documents */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Source Documents</h3>
              <div className="space-y-3">
                {mockDocuments.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  >
                    <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-gray-500">
                        {doc.content_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Evaluation Actions */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Assessment</h3>
              <div className="space-y-3">
                <button className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">
                  <StarIcon className="h-4 w-4 mr-2" />
                  Create Evaluation
                </button>
                <button className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                  <ChartBarIcon className="h-4 w-4 mr-2" />
                  Compare Generations
                </button>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Quick Quality Check</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Accuracy</span>
                    <span className="text-xs text-gray-400">Not rated</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Relevance</span>
                    <span className="text-xs text-gray-400">Not rated</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Clarity</span>
                    <span className="text-xs text-gray-400">Not rated</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 