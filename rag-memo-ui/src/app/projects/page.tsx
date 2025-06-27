'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
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
  UserIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Project, TenantType, ProjectStatus } from '@/types';
import { api } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

export default function ProjectsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    tenant_type: '',
    status: '',
    visibility: '',
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // Fetch projects with filters
  const { data: projectsData, isLoading, error, refetch } = useQuery({
    queryKey: ['projects', searchQuery, filters],
    queryFn: () => api.getProjects({
      page_size: 50,
      search: searchQuery || undefined,
      tenant_type: filters.tenant_type || undefined,
      status: filters.status || undefined,
      visibility: filters.visibility || undefined,
    }),
    enabled: isAuthenticated,
    staleTime: 30 * 1000, // 30 seconds
  });

  const projects = projectsData?.items || [];

  const handleCreateProject = () => {
    router.push('/projects/create');
  };

  const handleProjectClick = (projectId: string) => {
    router.push(`/projects/${projectId}`);
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-yellow-100 text-yellow-800';
      case 'archived':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTenantTypeColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'hr':
        return 'bg-blue-100 text-blue-800';
      case 'coding':
        return 'bg-purple-100 text-purple-800';
      case 'financial_report':
        return 'bg-green-100 text-green-800';
      case 'deep_research':
        return 'bg-orange-100 text-orange-800';
      case 'qa_generation':
        return 'bg-indigo-100 text-indigo-800';
      case 'raw_rag':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTenantTypeDisplay = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'hr':
        return 'Human Resources';
      case 'coding':
        return 'Software Development';
      case 'financial_report':
        return 'Financial Analysis';
      case 'deep_research':
        return 'Research & Analysis';
      case 'qa_generation':
        return 'Q&A Generation';
      case 'raw_rag':
        return 'General RAG Tasks';
      default:
        return type || 'Unknown';
    }
  };

  const ProjectCard = ({ project }: { project: any }) => (
    <div
      onClick={() => handleProjectClick(project.id)}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
              {project.status || 'Active'}
            </span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTenantTypeColor(project.tenant_type)}`}>
              {getTenantTypeDisplay(project.tenant_type)}
            </span>
          </div>
          <EyeIcon className="h-5 w-5 text-gray-400" />
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">
          {project.name}
        </h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {project.description || 'No description available'}
        </p>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <DocumentTextIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">{project.document_count || 0}</span>
            </div>
            <p className="text-xs text-gray-500">Documents</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <CpuChipIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">{project.element_count || 0}</span>
            </div>
            <p className="text-xs text-gray-500">Elements</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <SparklesIcon className="h-4 w-4 text-gray-500 mr-1" />
              <span className="text-sm font-medium text-gray-900">{project.generation_count || 0}</span>
            </div>
            <p className="text-xs text-gray-500">Generations</p>
          </div>
        </div>

        {/* Owner Information */}
        {project.owner_name && (
          <div className="mb-4 pb-4 border-b border-gray-100">
            <div className="flex items-center text-xs text-gray-600">
              <UserIcon className="h-3 w-3 mr-1" />
              <span className="font-medium">{project.owner_name}</span>
              {project.owner_email && (
                <span className="ml-1">({project.owner_email})</span>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center">
            <CalendarIcon className="h-3 w-3 mr-1" />
            {new Date(project.created_at).toLocaleDateString()}
          </div>
          <div className="flex items-center">
            {project.collaborators && project.collaborators.length > 0 && (
              <span>{project.collaborators.length + 1} members</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  // Compact List Item Component
  const ProjectListItem = ({ project }: { project: any }) => (
    <div
      onClick={() => handleProjectClick(project.id)}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
    >
      <div className="p-4">
        <div className="flex items-center justify-between">
          {/* Left side - Project info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {project.name}
              </h3>
              <div className="flex items-center space-x-2">
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                  {project.status || 'Active'}
                </span>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getTenantTypeColor(project.tenant_type)}`}>
                  {getTenantTypeDisplay(project.tenant_type)}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-6 text-xs text-gray-600 mb-2">
              {/* Owner */}
              {project.owner_name && (
                <div className="flex items-center">
                  <UserIcon className="h-3 w-3 mr-1" />
                  <span>{project.owner_name}</span>
                </div>
              )}
              
              {/* Created date */}
              <div className="flex items-center">
                <CalendarIcon className="h-3 w-3 mr-1" />
                <span>{new Date(project.created_at).toLocaleDateString()}</span>
              </div>
              
              {/* Members */}
              {project.collaborators && project.collaborators.length > 0 && (
                <span>{project.collaborators.length + 1} members</span>
              )}
            </div>
            
            <p className="text-gray-600 text-sm truncate">
              {project.description || 'No description available'}
            </p>
          </div>

          {/* Right side - Statistics */}
          <div className="flex items-center space-x-6 ml-6">
            <div className="text-center">
              <div className="flex items-center justify-center">
                <DocumentTextIcon className="h-4 w-4 text-gray-500 mr-1" />
                <span className="text-sm font-medium text-gray-900">{project.document_count || 0}</span>
              </div>
              <p className="text-xs text-gray-500">Docs</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center">
                <CpuChipIcon className="h-4 w-4 text-gray-500 mr-1" />
                <span className="text-sm font-medium text-gray-900">{project.element_count || 0}</span>
              </div>
              <p className="text-xs text-gray-500">Elements</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center">
                <SparklesIcon className="h-4 w-4 text-gray-500 mr-1" />
                <span className="text-sm font-medium text-gray-900">{project.generation_count || 0}</span>
              </div>
              <p className="text-xs text-gray-500">Gens</p>
            </div>
            <EyeIcon className="h-5 w-5 text-gray-400" />
          </div>
        </div>
      </div>
    </div>
  );

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

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
                  onChange={(e) => setFilters({ ...filters, tenant_type: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  <option value="hr">Human Resources</option>
                  <option value="coding">Software Development</option>
                  <option value="financial_report">Financial Analysis</option>
                  <option value="deep_research">Research & Analysis</option>
                  <option value="qa_generation">Q&A Generation</option>
                  <option value="raw_rag">General RAG Tasks</option>
                </select>

                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="archived">Archived</option>
                </select>

                <select
                  value={filters.visibility}
                  onChange={(e) => setFilters({ ...filters, visibility: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Visibility</option>
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                </select>
              </div>

              {/* View Mode Toggle */}
              <div className="flex rounded-md shadow-sm">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-2 text-sm font-medium border border-r-0 rounded-l-md ${
                    viewMode === 'grid'
                      ? 'bg-blue-50 text-blue-700 border-blue-200'
                      : 'bg-white text-gray-500 border-gray-300 hover:text-gray-700'
                  }`}
                >
                  <Squares2X2Icon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 text-sm font-medium border rounded-r-md ${
                    viewMode === 'list'
                      ? 'bg-blue-50 text-blue-700 border-blue-200'
                      : 'bg-white text-gray-500 border-gray-300 hover:text-gray-700'
                  }`}
                >
                  <ListBulletIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Projects Content */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow border border-gray-200 p-6">
                <div className="animate-pulse">
                  <div className="flex space-x-2 mb-4">
                    <div className="h-5 bg-gray-200 rounded-full w-16"></div>
                    <div className="h-5 bg-gray-200 rounded-full w-20"></div>
                  </div>
                  <div className="h-6 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded mb-4"></div>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="h-8 bg-gray-200 rounded"></div>
                    <div className="h-8 bg-gray-200 rounded"></div>
                    <div className="h-8 bg-gray-200 rounded"></div>
                  </div>
                  <div className="h-3 bg-gray-200 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading projects</h3>
            <p className="mt-1 text-sm text-gray-500">
              {error instanceof Error ? error.message : 'Something went wrong'}
            </p>
            <div className="mt-6">
              <button
                onClick={() => refetch()}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          </div>
        ) : projects.length === 0 ? (
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
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
            : 'space-y-4'
          }>
            {projects.map((project) => 
              viewMode === 'grid' ? (
                <ProjectCard key={project.id} project={project} />
              ) : (
                <ProjectListItem key={project.id} project={project} />
              )
            )}
          </div>
        )}

        {/* Load More / Pagination */}
        {projects.length > 0 && projectsData?.has_next && (
          <div className="mt-8 text-center">
            <button
              onClick={() => {/* Implement load more */}}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Load More Projects
            </button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
} 