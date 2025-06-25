'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  Squares2X2Icon,
  ListBulletIcon,
  FolderIcon,
  DocumentTextIcon,
  CpuChipIcon,
  SparklesIcon,
  EyeIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Project, TenantType, ProjectStatus } from '@/types';

export default function ProjectsPage() {
  const router = useRouter();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    tenant_type: '',
    status: '',
    visibility: '',
  });

  // Mock projects data - replace with actual API call
  const projects: Project[] = [
    {
      id: '1',
      name: 'Customer Support Knowledge Base',
      description: 'AI-powered customer support with FAQ processing and automated response generation.',
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
    },
    {
      id: '2',
      name: 'Product Documentation Assistant',
      description: 'Technical documentation processing and developer Q&A automation.',
      tenant_type: TenantType.ORGANIZATION,
      status: ProjectStatus.ACTIVE,
      keywords: ['documentation', 'technical', 'developers'],
      visibility: 'PUBLIC' as any,
      owner_id: '1',
      collaborators: [],
      document_count: 45,
      element_count: 12,
      generation_count: 89,
      created_at: '2024-12-18T09:15:00Z',
      updated_at: '2024-12-24T11:45:00Z'
    }
  ];

  const handleCreateProject = () => {
    router.push('/projects/create');
  };

  const handleProjectClick = (projectId: string) => {
    router.push(`/projects/${projectId}`);
  };

  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.ACTIVE:
        return 'bg-green-100 text-green-800';
      case ProjectStatus.INACTIVE:
        return 'bg-yellow-100 text-yellow-800';
      case ProjectStatus.ARCHIVED:
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTenantTypeColor = (type: TenantType) => {
    switch (type) {
      case TenantType.INDIVIDUAL:
        return 'bg-blue-100 text-blue-800';
      case TenantType.TEAM:
        return 'bg-purple-100 text-purple-800';
      case TenantType.ORGANIZATION:
        return 'bg-orange-100 text-orange-800';
      case TenantType.ENTERPRISE:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const ProjectCard = ({ project }: { project: Project }) => (
    <div
      onClick={() => handleProjectClick(project.id)}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
              {project.status}
            </span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTenantTypeColor(project.tenant_type)}`}>
              {project.tenant_type}
            </span>
          </div>
          <EyeIcon className="h-5 w-5 text-gray-400" />
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">
          {project.name}
        </h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {project.description}
        </p>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <DocumentTextIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">{project.document_count}</span>
            </div>
            <p className="text-xs text-gray-500">Documents</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <CpuChipIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">{project.element_count}</span>
            </div>
            <p className="text-xs text-gray-500">Elements</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <SparklesIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">{project.generation_count}</span>
            </div>
            <p className="text-xs text-gray-500">Generations</p>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center">
            <CalendarIcon className="h-3 w-3 mr-1" />
            {new Date(project.created_at).toLocaleDateString()}
          </div>
          <div className="flex items-center">
            {project.collaborators.length > 0 && (
              <span>{project.collaborators.length + 1} members</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <DashboardLayout title="Projects">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-gray-600">
              Manage your RAG projects and collaborate with your team.
            </p>
          </div>
          <button
            onClick={handleCreateProject}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            New Project
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
                    placeholder="Search projects..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Filters */}
              <div className="flex gap-3">
                <select
                  value={filters.tenant_type}
                  onChange={(e) => setFilters(prev => ({ ...prev, tenant_type: e.target.value }))}
                  className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  <option value="individual">Individual</option>
                  <option value="team">Team</option>
                  <option value="organization">Organization</option>
                  <option value="enterprise">Enterprise</option>
                </select>

                <select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  className="block px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="archived">Archived</option>
                </select>

                {/* View Toggle */}
                <div className="flex border border-gray-300 rounded-md">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 ${viewMode === 'grid' ? 'bg-blue-50 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
                  >
                    <Squares2X2Icon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 border-l ${viewMode === 'list' ? 'bg-blue-50 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
                  >
                    <ListBulletIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Projects Grid/List */}
        {projects.length > 0 ? (
          <div className={`grid gap-6 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'}`}>
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No projects found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first RAG project.
            </p>
            <div className="mt-6">
              <button
                onClick={handleCreateProject}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                Create Project
              </button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
} 