'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  SparklesIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  CpuChipIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  XCircleIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Generation, GenerationStatus, PaginatedResponse } from '@/types';
import { api } from '@/services/api';

function GenerationsPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<GenerationStatus | ''>('');
  const [dateRange, setDateRange] = useState('all');
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Get URL parameters
  const projectId = searchParams?.get('project_id');
  const executionId = searchParams?.get('execution_id');

  // Fetch generations from API
  const fetchGenerations = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const params: any = {
        page: currentPage,
        page_size: pageSize,
      };

      // Add filters based on URL parameters and user selections
      if (projectId) {
        params.project_id = projectId;
      }
      if (executionId) {
        params.execution_id = executionId;
      }
      if (selectedStatus) {
        params.status = selectedStatus;
      }
      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }

      console.log('Fetching generations with params:', params);
      const response: PaginatedResponse<Generation> = await api.getGenerations(params);
      
      setGenerations(response.items || []);
      setTotalCount(response.total_count || 0);
      
    } catch (err: any) {
      console.error('Failed to fetch generations:', err);
      setError('Failed to load generations. Please try again.');
      setGenerations([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch data when component mounts or filters change
  useEffect(() => {
    fetchGenerations();
  }, [currentPage, selectedStatus, projectId, executionId]);

  // Debounced search effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (currentPage === 1) {
        fetchGenerations();
      } else {
        setCurrentPage(1); // This will trigger fetchGenerations via the dependency array
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleGenerationClick = (generationId: string) => {
    router.push(`/generations/${generationId}`);
  };

  const getStatusIcon = (status: GenerationStatus) => {
    switch (status) {
      case GenerationStatus.COMPLETED:
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case GenerationStatus.FAILED:
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case GenerationStatus.PROCESSING:
        return (
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full" />
        );
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: GenerationStatus) => {
    switch (status) {
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

  const filteredGenerations = generations.filter(generation => {
    // If no search query, include all generations
    if (!searchQuery.trim()) {
      return true;
    }
    
    // Search in available fields
    const searchLower = searchQuery.toLowerCase();
    const matchesSearch = 
      (generation.element_name?.toLowerCase().includes(searchLower)) ||
      (generation.model_used?.toLowerCase().includes(searchLower)) ||
      (generation.id?.toLowerCase().includes(searchLower)) ||
      (generation.element_id?.toLowerCase().includes(searchLower));
    
    return matchesSearch;
  });

  const GenerationCard = ({ generation }: { generation: Generation }) => (
    <div
      onClick={() => handleGenerationClick(generation.id)}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            {getStatusIcon(generation.status)}
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(generation.status)}`}>
              {generation.status}
            </span>
          </div>
          <div className="text-xs text-gray-500">
            {new Date(generation.created_at).toLocaleString()}
          </div>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {generation.element_name || 'Unknown Element'}
        </h3>

        {generation.status === GenerationStatus.COMPLETED && generation.output_text && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {generation.output_text}
          </p>
        )}

        {generation.status === GenerationStatus.FAILED && generation.error_message && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700 text-sm">{generation.error_message}</p>
          </div>
        )}

        {generation.status === GenerationStatus.PROCESSING && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-blue-700 text-sm">Generation in progress...</p>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <CpuChipIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">{generation.tokens_used || 0}</span>
            </div>
            <p className="text-xs text-gray-500">Tokens</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <ClockIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">
                {generation.execution_time > 0 ? `${generation.execution_time}s` : '—'}
              </span>
            </div>
            <p className="text-xs text-gray-500">Time</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <span className="text-sm font-medium text-gray-900">
                ${generation.cost > 0 ? generation.cost.toFixed(4) : '—'}
              </span>
            </div>
            <p className="text-xs text-gray-500">Cost</p>
          </div>
        </div>
      </div>
    </div>
  );

  const completedGenerations = generations.filter(g => g.status === GenerationStatus.COMPLETED);
  const totalTokens = generations.reduce((sum, g) => sum + (g.tokens_used || 0), 0);
  const totalCost = generations.reduce((sum, g) => sum + (g.cost || 0), 0);
  const avgExecutionTime = completedGenerations.length > 0 
    ? completedGenerations.reduce((sum, g) => sum + (g.execution_time || 0), 0) / completedGenerations.length 
    : 0;

  if (isLoading) {
    return (
      <DashboardLayout title="Generations">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading generations...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Generations">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <p className="text-gray-600">
            Monitor and manage all AI generations across your projects.
            {projectId && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Filtered by Project: {projectId}
              </span>
            )}
            {executionId && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Execution: {executionId}
              </span>
            )}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700">{error}</p>
            <button 
              onClick={fetchGenerations}
              className="mt-2 text-sm text-red-600 hover:text-red-500 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <SparklesIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Generations
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {totalCount}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CpuChipIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Tokens
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {totalTokens.toLocaleString()}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-6 w-6 text-orange-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Avg Time
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {avgExecutionTime > 0 ? `${avgExecutionTime.toFixed(1)}s` : '—'}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Cost
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      ${totalCost.toFixed(4)}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search generations..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
                  />
                </div>
              </div>

              {/* Status Filter */}
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as GenerationStatus | '')}
                className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
              >
                <option value="">All Status</option>
                <option value={GenerationStatus.COMPLETED}>Completed</option>
                <option value={GenerationStatus.PROCESSING}>Processing</option>
                <option value={GenerationStatus.FAILED}>Failed</option>
              </select>

              {/* Date Range Filter */}
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
              </select>

              {/* Refresh Button */}
              <button
                onClick={fetchGenerations}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Generations List */}
        {filteredGenerations.length > 0 ? (
          <div className="space-y-4">
            {filteredGenerations.map((generation) => (
              <GenerationCard key={generation.id} generation={generation} />
            ))}
            
            {/* Pagination */}
            {totalCount > pageSize && (
              <div className="flex justify-center mt-8">
                <div className="flex space-x-2">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="px-3 py-2 text-sm text-gray-700">
                    Page {currentPage} of {Math.ceil(totalCount / pageSize)}
                  </span>
                  <button
                    onClick={() => setCurrentPage(p => p + 1)}
                    disabled={currentPage >= Math.ceil(totalCount / pageSize)}
                    className="px-3 py-2 bg-white border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <SparklesIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No generations found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchQuery || selectedStatus
                ? 'Try adjusting your filters.'
                : 'Start creating elements and generating content to see results here.'
              }
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

export default function GenerationsPage() {
  return (
    <Suspense fallback={
      <DashboardLayout title="Generations">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading generations...</p>
          </div>
        </div>
      </DashboardLayout>
    }>
      <GenerationsPageContent />
    </Suspense>
  );
} 