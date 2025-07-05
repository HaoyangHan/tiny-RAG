'use client';

import { useState, useEffect } from 'react';
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
import { api } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

interface GenerationDetailsProps {
  params: { id: string };
}

export default function GenerationDetailsPage({ params }: GenerationDetailsProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();
  const [generation, setGeneration] = useState<Generation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated && params.id) {
      fetchGenerationDetails();
    }
  }, [params.id, authLoading, isAuthenticated]);

  const fetchGenerationDetails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log('=== GENERATION DETAIL DEBUG ===');
      console.log('Fetching generation with ID:', params.id);
      
      const data = await api.getGeneration(params.id);
      
      console.log('Generation detail API response:', data);
      console.log('Available fields:', Object.keys(data));
      console.log('=== END DEBUG ===');
      
      setGeneration(data);
    } catch (err) {
      console.error('Failed to fetch generation details:', err);
      setError('Failed to load generation details. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyOutput = async () => {
    try {
      const outputText = generation?.output_text || (generation as any)?.content || '';
      await navigator.clipboard.writeText(outputText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const getStatusIcon = () => {
    if (!generation) return null;
    
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
    if (!generation) return 'bg-gray-100 text-gray-800';
    
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

  if (authLoading || isLoading) {
    return (
      <DashboardLayout title="Generation Details">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading generation details...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout title="Generation Details">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <ExclamationCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchGenerationDetails}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md"
            >
              Try Again
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!generation) {
    return (
      <DashboardLayout title="Generation Details">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <p className="text-gray-600">Generation not found.</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

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
                      From element: <span className="font-medium">
                        {generation.element_name || `Element ${generation.element_id?.slice(-8) || 'Unknown'}`}
                      </span>
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
                  <p className="text-lg font-semibold text-gray-900">
                    {(() => {
                      const timeMs = (generation as any).execution_time || (generation as any).generation_time_ms;
                      if (timeMs && timeMs > 0) {
                        return `${(timeMs / 1000).toFixed(1)}s`;
                      }
                      return '—';
                    })()}
                  </p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <CpuChipIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Tokens Used</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {((generation as any).tokens_used || (generation as any).token_usage || 0).toLocaleString()}
                  </p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <ChartBarIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Cost</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {(() => {
                      const cost = (generation as any).cost || (generation as any).cost_usd;
                      return cost && cost > 0 ? `$${cost.toFixed(4)}` : '$0.0000';
                    })()}
                  </p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <SparklesIcon className="h-5 w-5 text-gray-400 mx-auto mb-1" />
                  <p className="text-xs text-gray-500">Model</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {(generation as any).model_used || (generation as any).model_name || 'Unknown'}
                  </p>
                </div>
              </div>
            </div>

            {/* Input Data */}
            {(generation as any).input_data && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Input Data</h2>
                <div className="space-y-4">
                  {Object.entries((generation as any).input_data).map(([key, value]) => (
                    <div key={key}>
                      <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                        {key.replace('_', ' ')}
                      </label>
                      <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
                        <p className="text-sm text-gray-900">{String(value)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Generated Output */}
            {(generation.output_text || (generation as any).content) && (
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-medium text-gray-900">Generated Output</h2>
                  <button
                    onClick={handleCopyOutput}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <ClipboardDocumentIcon className="h-4 w-4 mr-1.5" />
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
                  <pre className="text-sm text-gray-900 whitespace-pre-wrap">
                    {generation.output_text || (generation as any).content}
                  </pre>
                </div>
              </div>
            )}

            {/* Error Message */}
            {generation.status === GenerationStatus.FAILED && generation.error_message && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Error Details</h2>
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <p className="text-sm text-red-700">{generation.error_message}</p>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Generation Info */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Generation Info</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-500">ID</p>
                  <p className="text-sm text-gray-900 break-all">{generation.id}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Created</p>
                  <p className="text-sm text-gray-900">
                    {new Date(generation.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Element</p>
                  <a
                    href={`/elements/${generation.element_id}`}
                    className="text-sm text-blue-600 hover:text-blue-500"
                  >
                    {generation.element_name || `Element ${generation.element_id?.slice(-8) || 'Unknown'}`}
                  </a>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500">Project</p>
                  <a
                    href={`/projects/${generation.project_id}`}
                    className="text-sm text-blue-600 hover:text-blue-500"
                  >
                    View Project
                  </a>
                </div>
              </div>
            </div>

            {/* Quality Assessment */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Assessment</h3>
              <div className="space-y-3">
                <button className="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md text-sm font-medium">
                  <StarIcon className="h-4 w-4 inline mr-2" />
                  Create Evaluation
                </button>
                <button className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-md text-sm font-medium">
                  <ChartBarIcon className="h-4 w-4 inline mr-2" />
                  Compare Generations
                </button>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Quick Quality Check</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-500">Accuracy</span>
                    <span className="text-xs text-gray-400">Not rated</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-xs text-gray-500">Relevance</span>
                    <span className="text-xs text-gray-400">Not rated</span>
                  </div>
                  <div className="flex justify-between">
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