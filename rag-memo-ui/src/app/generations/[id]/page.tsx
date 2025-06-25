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
  const generation: Generation = {
    id: params.id,
    element_id: '1',
    element_name: 'Customer FAQ Template',
    status: GenerationStatus.COMPLETED,
    input_data: {
      context: 'Our return policy allows customers to return products within 30 days of purchase for a full refund. Products must be in original condition with all packaging and accessories. Digital products cannot be returned after download. Shipping costs for returns are covered by the customer unless the item was defective.',
      question: 'Can I return my product after 2 weeks if I\'m not satisfied?'
    },
    output_text: `Yes, you can definitely return your product after 2 weeks if you're not satisfied! According to our return policy, you have a full 30 days from the date of purchase to return any product for a complete refund.

Here are the key requirements for your return:
• The product must be in its original condition
• All original packaging and accessories must be included
• You'll need your original receipt or order confirmation

To initiate a return:
1. Contact our customer service team at returns@company.com
2. Include your order number and reason for return
3. We'll provide a return shipping label
4. Pack the item securely and ship it back to us

Please note that while we cover return shipping for defective items, standard returns require the customer to cover shipping costs. Your refund will be processed within 5-7 business days after we receive the returned item.

Is there anything specific about your purchase that's causing dissatisfaction? We're always happy to help resolve any issues!`,
    model_used: 'gpt-4-turbo',
    tokens_used: 487,
    execution_time: 3.2,
    cost: 0.0245,
    project_id: '1',
    created_at: '2024-12-25T14:20:00Z',
    updated_at: '2024-12-25T14:20:00Z',
    error_message: null
  };

  // Mock source documents
  const sourceDocuments: Document[] = [
    {
      id: '1',
      title: 'Return Policy Documentation',
      content: 'Our return policy allows customers to return products within 30 days...',
      filename: 'return-policy.pdf',
      file_type: 'pdf',
      file_size: 245760,
      status: 'PROCESSED' as any,
      project_id: '1',
      created_at: '2024-12-20T10:30:00Z',
      updated_at: '2024-12-20T10:35:00Z'
    },
    {
      id: '2',
      title: 'Customer Service Guidelines',
      content: 'Customer service representatives should always...',
      filename: 'customer-service-guide.docx',
      file_type: 'docx',
      file_size: 128000,
      status: 'PROCESSED' as any,
      project_id: '1',
      created_at: '2024-12-18T09:15:00Z',
      updated_at: '2024-12-18T09:20:00Z'
    }
  ];

  const handleCopyOutput = async () => {
    try {
      await navigator.clipboard.writeText(generation.output_text || '');
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const getStatusIcon = () => {
    switch (generation.status) {
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
    switch (generation.status) {
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
                      From element: <span className="font-medium">{generation.element_name}</span>
                    </p>
                  </div>
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor()}`}>
                  {generation.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <ClockIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Execution Time</p>
                  <p className="text-lg font-semibold text-gray-900">{generation.execution_time}s</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <CpuChipIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Tokens Used</p>
                  <p className="text-lg font-semibold text-gray-900">{generation.tokens_used.toLocaleString()}</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <ChartBarIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Cost</p>
                  <p className="text-lg font-semibold text-gray-900">${generation.cost.toFixed(4)}</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <SparklesIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Model</p>
                  <p className="text-lg font-semibold text-gray-900">{generation.model_used}</p>
                </div>
              </div>
            </div>

            {/* Input Data */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Input Data</h2>
              <div className="space-y-4">
                {Object.entries(generation.input_data).map(([key, value]) => (
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
            {generation.status === GenerationStatus.COMPLETED && generation.output_text && (
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
                      {generation.output_text}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {generation.status === GenerationStatus.FAILED && generation.error_message && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Error Details</h2>
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="flex">
                    <ExclamationCircleIcon className="h-5 w-5 text-red-400 mr-2 mt-0.5" />
                    <div className="text-sm text-red-700">
                      <p className="font-medium">Generation Failed</p>
                      <p className="mt-1">{generation.error_message}</p>
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
                      <span className="font-medium">{Math.floor(generation.tokens_used * 0.6).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Output Tokens</span>
                      <span className="font-medium">{Math.floor(generation.tokens_used * 0.4).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm border-t pt-2">
                      <span className="text-gray-700 font-medium">Total Tokens</span>
                      <span className="font-semibold">{generation.tokens_used.toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-3">Cost Analysis</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Input Cost</span>
                      <span className="font-medium">${(generation.cost * 0.6).toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Output Cost</span>
                      <span className="font-medium">${(generation.cost * 0.4).toFixed(4)}</span>
                    </div>
                    <div className="flex justify-between text-sm border-t pt-2">
                      <span className="text-gray-700 font-medium">Total Cost</span>
                      <span className="font-semibold">${generation.cost.toFixed(4)}</span>
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
                  <p className="text-sm text-gray-900 font-mono">{generation.id}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Created</p>
                  <p className="text-sm text-gray-900">
                    {new Date(generation.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Element</p>
                  <button
                    onClick={() => router.push(`/elements/${generation.element_id}`)}
                    className="text-sm text-blue-600 hover:text-blue-500 flex items-center"
                  >
                    {generation.element_name}
                    <LinkIcon className="h-3 w-3 ml-1" />
                  </button>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Project</p>
                  <button
                    onClick={() => router.push(`/projects/${generation.project_id}`)}
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
                {sourceDocuments.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                  >
                    <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {doc.title}
                      </p>
                      <p className="text-xs text-gray-500">
                        {doc.file_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB
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