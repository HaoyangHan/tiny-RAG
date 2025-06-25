'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
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
import { Generation, GenerationStatus } from '@/types';

export default function GenerationsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<GenerationStatus | ''>('');
  const [dateRange, setDateRange] = useState('all');

  // Mock generations data - replace with actual API call
  const generations: Generation[] = [
    {
      id: '1',
      element_id: '1',
      element_name: 'Customer FAQ Template',
      status: GenerationStatus.COMPLETED,
      input_data: {
        context: 'Product return policy allows returns within 30 days...',
        question: 'Can I return my product after 2 weeks?'
      },
      output_text: 'Yes, you can return your product after 2 weeks. Our return policy allows returns within 30 days of purchase...',
      model_used: 'gpt-4-turbo',
      tokens_used: 245,
      execution_time: 2.3,
      cost: 0.012,
      project_id: '1',
      created_at: '2024-12-25T14:20:00Z',
      updated_at: '2024-12-25T14:20:00Z',
      error_message: null
    },
    {
      id: '2',
      element_id: '2',
      element_name: 'Documentation Search Tool',
      status: GenerationStatus.PROCESSING,
      input_data: {
        query: 'API authentication methods',
        category: 'technical'
      },
      output_text: null,
      model_used: 'gpt-4-turbo',
      tokens_used: 0,
      execution_time: 0,
      cost: 0,
      project_id: '2',
      created_at: '2024-12-25T14:22:00Z',
      updated_at: '2024-12-25T14:22:00Z',
      error_message: null
    },
    {
      id: '3',
      element_id: '1',
      element_name: 'Customer FAQ Template',
      status: GenerationStatus.FAILED,
      input_data: {
        context: '',
        question: 'What is your refund policy?'
      },
      output_text: null,
      model_used: 'gpt-4-turbo',
      tokens_used: 0,
      execution_time: 0,
      cost: 0,
      project_id: '1',
      created_at: '2024-12-25T14:18:00Z',
      updated_at: '2024-12-25T14:18:00Z',
      error_message: 'Context cannot be empty'
    }
  ];

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
    const matchesSearch = generation.element_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         generation.model_used.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !selectedStatus || generation.status === selectedStatus;
    
    // Date filtering logic would go here
    
    return matchesSearch && matchesStatus;
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
          {generation.element_name}
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
              <span className="text-sm font-medium text-gray-900">{generation.tokens_used}</span>
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
  const totalTokens = generations.reduce((sum, g) => sum + g.tokens_used, 0);
  const totalCost = generations.reduce((sum, g) => sum + g.cost, 0);
  const avgExecutionTime = completedGenerations.length > 0 
    ? completedGenerations.reduce((sum, g) => sum + g.execution_time, 0) / completedGenerations.length 
    : 0;

  return (
    <DashboardLayout title="Generations">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <p className="text-gray-600">
            Monitor and manage all AI generations across your projects.
          </p>
        </div>

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
                      {generations.length}
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
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Status Filter */}
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as GenerationStatus | '')}
                className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
              </select>
            </div>
          </div>
        </div>

        {/* Generations List */}
        {filteredGenerations.length > 0 ? (
          <div className="space-y-4">
            {filteredGenerations.map((generation) => (
              <GenerationCard key={generation.id} generation={generation} />
            ))}
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