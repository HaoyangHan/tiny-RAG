'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ChevronLeftIcon,
  DocumentTextIcon,
  CpuChipIcon,
  SparklesIcon,
  Cog6ToothIcon,
  EyeIcon,
  UsersIcon,
  CalendarIcon,
  ChartBarIcon,
  PlusIcon,
  FolderOpenIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Project, TenantType, ProjectStatus, Document, Element, Generation } from '@/types';

interface ProjectDetailsProps {
  params: { id: string };
}

export default function ProjectDetailsPage({ params }: ProjectDetailsProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');

  // Mock project data - replace with actual API call
  const project: Project = {
    id: params.id,
    name: 'Customer Support Knowledge Base',
    description: 'AI-powered customer support with FAQ processing and automated response generation for improved customer experience.',
    tenant_type: TenantType.TEAM,
    status: ProjectStatus.ACTIVE,
    keywords: ['customer-support', 'faq', 'automation'],
    visibility: 'PRIVATE' as any,
    owner_id: '1',
    collaborators: ['2', '3'],
    document_count: 24,
    element_count: 8,
    generation_count: 156,
    created_at: '2024-12-20T10:30:00Z',
    updated_at: '2024-12-25T14:20:00Z'
  };

  // Mock related data
  const recentDocuments: Document[] = [
    {
      id: '1',
      title: 'Return Policy FAQ.pdf',
      content: 'Our return policy allows...',
      filename: 'return-policy-faq.pdf',
      file_type: 'pdf',
      file_size: 245760,
      status: 'PROCESSED' as any,
      project_id: params.id,
      created_at: '2024-12-24T15:30:00Z',
      updated_at: '2024-12-24T15:35:00Z'
    },
    {
      id: '2', 
      title: 'Shipping Information.docx',
      content: 'Shipping times and costs...',
      filename: 'shipping-info.docx',
      file_type: 'docx',
      file_size: 128000,
      status: 'PROCESSED' as any,
      project_id: params.id,
      created_at: '2024-12-23T10:15:00Z',
      updated_at: '2024-12-23T10:20:00Z'
    }
  ];

  const recentElements: Element[] = [
    {
      id: '1',
      name: 'Customer FAQ Template',
      description: 'Template for generating customer FAQ responses',
      type: 'PROMPT_TEMPLATE' as any,
      status: 'ACTIVE' as any,
      template_content: 'Based on context: {context}\nAnswer: {question}',
      variables: [],
      project_id: params.id,
      created_at: '2024-12-22T14:00:00Z',
      updated_at: '2024-12-25T09:30:00Z',
      execution_count: 89,
      last_executed: '2024-12-25T09:30:00Z'
    }
  ];

  const recentGenerations: Generation[] = [
    {
      id: '1',
      element_id: '1',
      element_name: 'Customer FAQ Template',
      status: 'COMPLETED' as any,
      input_data: { context: 'Return policy...', question: 'Can I return after 2 weeks?' },
      output_text: 'Yes, you can return your product after 2 weeks...',
      model_used: 'gpt-4-turbo',
      tokens_used: 245,
      execution_time: 2.3,
      cost: 0.012,
      project_id: params.id,
      created_at: '2024-12-25T14:20:00Z',
      updated_at: '2024-12-25T14:20:00Z',
      error_message: null
    }
  ];

  const tabs = [
    { id: 'overview', name: 'Overview', icon: FolderOpenIcon },
    { id: 'documents', name: 'Documents', icon: DocumentTextIcon },
    { id: 'elements', name: 'Elements', icon: CpuChipIcon },
    { id: 'generations', name: 'Generations', icon: SparklesIcon },
    { id: 'settings', name: 'Settings', icon: Cog6ToothIcon },
  ];

  // Project overview render function
  const renderProjectOverview = () => (
    <div className="space-y-6">
      {/* Project Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Documents</p>
                <p className="text-2xl font-semibold text-gray-900">{project.document_count}</p>
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
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Elements</p>
                <p className="text-2xl font-semibold text-gray-900">{project.element_count}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <SparklesIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Generations</p>
                <p className="text-2xl font-semibold text-gray-900">{project.generation_count}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UsersIcon className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Team Members</p>
                <p className="text-2xl font-semibold text-gray-900">{project.collaborators.length + 1}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Recent Documents</h3>
              <button
                onClick={() => setActiveTab('documents')}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                View all
              </button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentDocuments.map((doc) => (
              <div key={doc.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{doc.title}</p>
                      <p className="text-xs text-gray-500">
                        {(doc.file_size / 1024).toFixed(1)} KB • {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Processed
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Elements */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Recent Elements</h3>
              <button
                onClick={() => setActiveTab('elements')}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                View all
              </button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentElements.map((element) => (
              <div key={element.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <CpuChipIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{element.name}</p>
                      <p className="text-xs text-gray-500">
                        {element.execution_count} executions • {new Date(element.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Project Description */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">About This Project</h3>
        <p className="text-gray-600 mb-4">{project.description}</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm font-medium text-gray-500">Keywords</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {project.keywords.map((keyword) => (
                <span
                  key={keyword}
                  className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-blue-100 text-blue-800"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Created</p>
            <p className="text-sm text-gray-900 mt-1">
              {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Last Updated</p>
            <p className="text-sm text-gray-900 mt-1">
              {new Date(project.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  // Project documents render function
  const renderProjectDocuments = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Project Documents</h3>
        <button
          onClick={() => router.push('/documents/upload')}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
          Upload Documents
        </button>
      </div>

      <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
        {recentDocuments.map((doc) => (
          <div key={doc.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                <div>
                  <h4 className="text-lg font-medium text-gray-900">{doc.title}</h4>
                  <p className="text-sm text-gray-500">
                    {doc.file_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Uploaded {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Processed
                </span>
                <button className="text-gray-400 hover:text-gray-600">
                  <EyeIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  // Project elements render function
  const renderProjectElements = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Project Elements</h3>
        <button
          onClick={() => router.push('/elements/create')}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
          Create Element
        </button>
      </div>

      <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
        {recentElements.map((element) => (
          <div key={element.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <CpuChipIcon className="h-8 w-8 text-gray-400" />
                <div>
                  <h4 className="text-lg font-medium text-gray-900">{element.name}</h4>
                  <p className="text-sm text-gray-500">{element.description}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {element.execution_count} executions • Last run {element.last_executed ? new Date(element.last_executed).toLocaleDateString() : 'Never'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {element.status}
                </span>
                <button className="text-gray-400 hover:text-gray-600">
                  <EyeIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderProjectOverview();
      case 'documents':
        return renderProjectDocuments();
      case 'elements':
        return renderProjectElements();
      case 'generations':
        return <div className="text-center py-8"><p className="text-gray-500">Generations view coming soon</p></div>;
      case 'settings':
        return <div className="text-center py-8"><p className="text-gray-500">Settings view coming soon</p></div>;
      default:
        return renderProjectOverview();
    }
  };

  return (
    <DashboardLayout title={project.name}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/projects')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to Projects
          </button>
        </div>

        {/* Project Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    project.status === ProjectStatus.ACTIVE ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {project.status}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {project.tenant_type}
                  </span>
                </div>
                <p className="text-gray-600">{project.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                  <UsersIcon className="h-4 w-4 mr-2" />
                  Collaborate
                </button>
                <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                  <Cog6ToothIcon className="h-4 w-4 mr-2" />
                  Settings
                </button>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-t border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </div>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {renderTabContent()}
      </div>
    </DashboardLayout>
  );
} 