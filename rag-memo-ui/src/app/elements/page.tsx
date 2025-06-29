'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  CpuChipIcon,
  DocumentTextIcon,
  WrenchScrewdriverIcon,
  Cog6ToothIcon,
  PlayIcon,
  ChartBarIcon,
  ClockIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Element, ElementType, ElementStatus } from '@/types';
import { api } from '@/services/api';

export default function ElementsPage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<ElementType | ''>('');
  const [selectedStatus, setSelectedStatus] = useState<ElementStatus | ''>('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // Fetch elements from API
  const {
    data: elementsData,
    isLoading: elementsLoading,
    error: elementsError,
    refetch: refetchElements
  } = useQuery({
    queryKey: ['elements', page, pageSize, selectedType, selectedStatus],
    queryFn: () => api.getElements({
      page,
      page_size: pageSize,
      element_type: selectedType || undefined,
      status: selectedStatus || undefined,
    }),
    staleTime: 30000, // 30 seconds
  });

  const elements = elementsData?.items || [];
  const totalElements = elementsData?.total_count || 0;

  const handleCreateElement = () => {
    router.push('/elements/create');
  };

  const handleElementClick = (elementId: string) => {
    router.push(`/elements/${elementId}`);
  };

  const handleDeleteElement = async (elementId: string, elementName: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent navigation when clicking delete
    
    if (window.confirm(`Are you sure you want to delete "${elementName}"? This action cannot be undone.`)) {
      try {
        await api.deleteElement(elementId);
        refetchElements(); // Refresh the elements list
      } catch (error) {
        console.error('Failed to delete element:', error);
        alert('Failed to delete element. Please try again.');
      }
    }
  };

  const getTypeIcon = (type: ElementType) => {
    switch (type) {
      case ElementType.PROMPT_TEMPLATE:
        return DocumentTextIcon;
      case ElementType.AGENTIC_TOOL:
        return WrenchScrewdriverIcon;
      case ElementType.MCP_CONFIG:
        return Cog6ToothIcon;
      default:
        return CpuChipIcon;
    }
  };

  const getTypeColor = (type: ElementType) => {
    switch (type) {
      case ElementType.PROMPT_TEMPLATE:
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case ElementType.AGENTIC_TOOL:
        return 'bg-green-100 text-green-800 border-green-200';
      case ElementType.MCP_CONFIG:
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: ElementStatus) => {
    switch (status) {
      case ElementStatus.ACTIVE:
        return 'bg-green-100 text-green-800';
      case ElementStatus.DRAFT:
        return 'bg-yellow-100 text-yellow-800';
      case ElementStatus.ARCHIVED:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredElements = elements.filter(element => {
    const matchesSearch = element.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (element.description || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = !selectedType || element.element_type === selectedType;
    const matchesStatus = !selectedStatus || element.status === selectedStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  const ElementCard = ({ element }: { element: Element }) => {
    const TypeIcon = getTypeIcon(element.element_type);
    
    return (
      <div
        onClick={() => handleElementClick(element.id)}
        className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg border ${getTypeColor(element.element_type)}`}>
                <TypeIcon className="h-5 w-5" />
              </div>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(element.status)}`}>
                {element.status}
              </span>
            </div>
            <span className="text-xs text-gray-500">{element.element_type}</span>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">
            {element.name}
          </h3>
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {element.description || 'No description provided'}
          </p>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <ChartBarIcon className="h-4 w-4 text-gray-500 mr-1" />
                <span className="text-sm font-medium text-gray-900">{element.execution_count || 0}</span>
              </div>
              <p className="text-xs text-gray-500">Executions</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <ClockIcon className="h-4 w-4 text-gray-500 mr-1" />
                <span className="text-sm font-medium text-gray-900">
                  {element.updated_at ? new Date(element.updated_at).toLocaleDateString() : 'Never'}
                </span>
              </div>
              <p className="text-xs text-gray-500">Last Updated</p>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              Created {new Date(element.created_at).toLocaleDateString()}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  console.log('Execute element:', element.id);
                }}
                className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <PlayIcon className="h-3 w-3 mr-1" />
                Execute
              </button>
              <button
                onClick={(e) => handleDeleteElement(element.id, element.name, e)}
                className="inline-flex items-center p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
                title="Delete element"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (elementsLoading) {
    return (
      <DashboardLayout title="Elements">
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  if (elementsError) {
    return (
      <DashboardLayout title="Elements">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <CpuChipIcon className="mx-auto h-12 w-12 text-red-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading elements</h3>
            <p className="mt-1 text-sm text-gray-500">
              Failed to fetch elements. Please try again.
            </p>
            <div className="mt-6">
              <button
                onClick={() => refetchElements()}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Elements">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-gray-600">
              Create and manage prompt templates, agentic tools, and MCP configurations.
            </p>
          </div>
          <button
            onClick={handleCreateElement}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            New Element
          </button>
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
                    placeholder="Search elements..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Type Filter */}
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value as ElementType | '')}
                className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option value={ElementType.PROMPT_TEMPLATE}>Prompt Template</option>
                <option value={ElementType.AGENTIC_TOOL}>Agentic Tool</option>
                <option value={ElementType.MCP_CONFIG}>MCP Config</option>
              </select>

              {/* Status Filter */}
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as ElementStatus | '')}
                className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Status</option>
                <option value={ElementStatus.ACTIVE}>Active</option>
                <option value={ElementStatus.DRAFT}>Draft</option>
                <option value={ElementStatus.ARCHIVED}>Archived</option>
              </select>
            </div>
          </div>
        </div>

        {/* Elements Grid or Empty State */}
        {filteredElements.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredElements.map((element) => (
              <ElementCard key={element.id} element={element} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <CpuChipIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No elements found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchQuery || selectedType || selectedStatus
                ? 'Try adjusting your filters.'
                : 'Get started by creating your first element.'
              }
            </p>
            {!searchQuery && !selectedType && !selectedStatus && (
              <div className="mt-6">
                <button
                  onClick={handleCreateElement}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                  Create Element
                </button>
              </div>
            )}
          </div>
        )}

        {/* Stats Summary */}
        {elements.length > 0 && (
          <div className="mt-8 bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Element Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {elements.filter(e => e.element_type === ElementType.PROMPT_TEMPLATE).length}
                </div>
                <div className="text-sm text-gray-500">Prompt Templates</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {elements.filter(e => e.element_type === ElementType.AGENTIC_TOOL).length}
                </div>
                <div className="text-sm text-gray-500">Agentic Tools</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {elements.filter(e => e.element_type === ElementType.MCP_CONFIG).length}
                </div>
                <div className="text-sm text-gray-500">MCP Configs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {elements.reduce((sum, e) => sum + (e.execution_count || 0), 0)}
                </div>
                <div className="text-sm text-gray-500">Total Executions</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
