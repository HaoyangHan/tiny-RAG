'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  ChevronLeftIcon,
  DocumentTextIcon,
  CpuChipIcon,
  WrenchScrewdriverIcon,
  Cog6ToothIcon,
  CalendarIcon,
  ChartBarIcon,
  ClockIcon,
  PlayIcon,
  PencilIcon,
  TagIcon,
  EyeIcon,
  CodeBracketIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Element, ElementType, ElementStatus } from '@/types';

// Extended element interface to match API response structure
interface ElementDetail extends Element {
  template_version?: string;
  template_content?: string;
  template_variables?: string[];
  execution_config?: Record<string, any>;
}
import { api } from '@/services/api';

interface ElementDetailsProps {
  params: { id: string };
}

export default function ElementDetailsPage({ params }: ElementDetailsProps) {
  const router = useRouter();
  const [element, setElement] = useState<ElementDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch element data
  useEffect(() => {
    const fetchElement = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const elementData = await api.getElement(params.id);
        setElement(elementData);
      } catch (error) {
        console.error('Failed to fetch element:', error);
        setError('Failed to load element details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchElement();
  }, [params.id]);

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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Element Info */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-gray-900">Element Information</h2>
          <button
            onClick={() => console.log('Edit element')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <PencilIcon className="h-4 w-4 mr-2" />
            Edit
          </button>
        </div>

        <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
          <div>
            <dt className="text-sm font-medium text-gray-500">Name</dt>
            <dd className="mt-1 text-sm text-gray-900">{element?.name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Type</dt>
            <dd className="mt-1">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(element?.element_type as ElementType)}`}>
                {element?.element_type}
              </span>
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Status</dt>
                         <dd className="mt-1">
               <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(element?.status as ElementStatus)}`}>
                 {element?.status}
              </span>
            </dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Version</dt>
            <dd className="mt-1 text-sm text-gray-900">{element?.template_version || 'N/A'}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-sm font-medium text-gray-500">Description</dt>
            <dd className="mt-1 text-sm text-gray-900">{element?.description || 'No description provided'}</dd>
          </div>
        </dl>
      </div>

      {/* Tags */}
      {element?.tags && element.tags.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {element.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800"
              >
                <TagIcon className="h-3 w-3 mr-1" />
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Usage Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{element?.execution_count || 0}</div>
            <div className="text-sm text-gray-600">Total Executions</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <ClockIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {element?.usage_statistics?.average_execution_time?.toFixed(1) || '—'}s
            </div>
            <div className="text-sm text-gray-600">Avg Time</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <SparklesIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {element?.usage_statistics?.success_rate ? `${(element.usage_statistics.success_rate * 100).toFixed(1)}%` : '—'}
            </div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <CpuChipIcon className="h-6 w-6 text-orange-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {element?.usage_statistics?.total_tokens_used?.toLocaleString() || '—'}
            </div>
            <div className="text-sm text-gray-600">Total Tokens</div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Timeline</h3>
        <div className="space-y-4">
          <div className="flex items-center">
            <CalendarIcon className="h-5 w-5 text-gray-400 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-900">Created</p>
              <p className="text-sm text-gray-600">{element?.created_at ? formatDate(element.created_at) : 'N/A'}</p>
            </div>
          </div>
          <div className="flex items-center">
            <CalendarIcon className="h-5 w-5 text-gray-400 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-900">Last Updated</p>
              <p className="text-sm text-gray-600">{element?.updated_at ? formatDate(element.updated_at) : 'N/A'}</p>
            </div>
          </div>
          {element?.usage_statistics?.last_executed && (
            <div className="flex items-center">
              <PlayIcon className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-900">Last Executed</p>
                <p className="text-sm text-gray-600">{formatDate(element.usage_statistics.last_executed)}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderTemplateTab = () => (
    <div className="space-y-6">
      {/* Template Content */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Template Content</h3>
          <button
            onClick={() => console.log('Edit template')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <PencilIcon className="h-4 w-4 mr-2" />
            Edit Template
          </button>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
            {element?.template_content || 'No template content available'}
          </pre>
        </div>
      </div>

      {/* Variables */}
      {element?.template_variables && element.template_variables.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Template Variables</h3>
          <div className="space-y-3">
            {element.template_variables.map((variable: string, index: number) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">
                    <CodeBracketIcon className="h-4 w-4 inline mr-1" />
                    {`{${variable}}`}
                  </span>
                  <span className="text-sm text-gray-600">Variable</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Execution Config */}
      {element?.execution_config && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Execution Configuration</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
              {JSON.stringify(element.execution_config, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );

  if (isLoading) {
    return (
      <DashboardLayout title="Element Details">
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  if (error || !element) {
    return (
      <DashboardLayout title="Element Details">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <CpuChipIcon className="mx-auto h-12 w-12 text-red-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Element not found</h3>
            <p className="mt-1 text-sm text-gray-600">
              {error || 'The element you are looking for does not exist.'}
            </p>
            <div className="mt-6">
              <button
                onClick={() => router.push('/elements')}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <ChevronLeftIcon className="h-4 w-4 mr-2" />
                Back to Elements
              </button>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const TypeIcon = getTypeIcon(element.element_type as ElementType);

  return (
    <DashboardLayout title={element.name}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/elements')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to Elements
          </button>
        </div>

        {/* Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-lg border ${getTypeColor(element.element_type as ElementType)}`}>
                  <TypeIcon className="h-6 w-6" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{element.name}</h1>
                  <p className="text-gray-600">{element.description}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => console.log('Execute element')}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Execute
                </button>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-t border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <EyeIcon className="h-4 w-4 inline mr-2" />
                Overview
              </button>
              <button
                onClick={() => setActiveTab('template')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'template'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <DocumentTextIcon className="h-4 w-4 inline mr-2" />
                Template
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'template' && renderTemplateTab()}
      </div>
    </DashboardLayout>
  );
} 