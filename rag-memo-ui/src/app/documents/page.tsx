/**
 * Global Documents Management Page
 * Route: /documents
 * TinyRAG v1.4.2 - Browse and manage documents across all projects
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  FolderOpenIcon,
  CalendarIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import { Document, Project } from '@/types';

// Document status mapping
const getStatusIcon = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return <CheckCircleIcon className="h-4 w-4 text-green-600" />;
    case 'processing':
      return <ArrowPathIcon className="h-4 w-4 text-blue-600 animate-spin" />;
    case 'failed':
      return <ExclamationCircleIcon className="h-4 w-4 text-red-600" />;
    case 'pending':
    default:
      return <ClockIcon className="h-4 w-4 text-yellow-600" />;
  }
};

const getStatusText = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return 'Processed';
    case 'processing':
      return 'Processing';
    case 'failed':
      return 'Failed';
    case 'pending':
    default:
      return 'Pending';
  }
};

const getStatusColor = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'processing':
      return 'bg-blue-100 text-blue-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    case 'pending':
    default:
      return 'bg-yellow-100 text-yellow-800';
  }
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export default function DocumentsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProject, setSelectedProject] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // Fetch projects for filtering
  const { data: projectsData } = useQuery({
    queryKey: ['projects'],
    queryFn: () => api.getProjects({ page_size: 100 }),
    enabled: isAuthenticated,
  });

  const projects = projectsData?.items || [];

  // Fetch documents with filtering
  const { data: documentsData, isLoading: documentsLoading, refetch: refetchDocuments } = useQuery({
    queryKey: ['all-documents', currentPage, searchTerm, selectedProject, selectedStatus],
    queryFn: () => api.getDocuments({
      page: currentPage,
      page_size: pageSize,
      project_id: selectedProject || undefined,
    }),
    enabled: isAuthenticated,
    refetchInterval: 10000, // Refresh every 10 seconds for status updates
  });

  const documents = documentsData?.items || [];
  const totalDocuments = documentsData?.total_count || 0;
  const totalPages = Math.ceil(totalDocuments / pageSize);

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = !searchTerm || 
      doc.filename.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesProject = !selectedProject || doc.project_id === selectedProject;
    const matchesStatus = !selectedStatus || doc.status === selectedStatus;
    
    return matchesSearch && matchesProject && matchesStatus;
  });

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedProject('');
    setSelectedStatus('');
    setCurrentPage(1);
  };

  const handleDocumentClick = (document: Document) => {
    router.push(`/projects/${document.project_id}`);
  };

  const handleDeleteDocument = async (documentId: string, fileName: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent navigation when clicking delete
    
    if (window.confirm(`Are you sure you want to delete "${fileName}"? This action cannot be undone.`)) {
      try {
        await api.deleteDocument(documentId);
        refetchDocuments(); // Refresh the documents list
      } catch (error) {
        console.error('Failed to delete document:', error);
        alert('Failed to delete document. Please try again.');
      }
    }
  };

  const handleUploadClick = () => {
    // If user has projects, redirect to first project's upload page
    if (projects.length > 0) {
      router.push(`/projects/${projects[0].id}/document-upload`);
    } else {
      // No projects, redirect to create project
      router.push('/projects/create');
    }
  };

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
    <DashboardLayout title="Document Management">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <DocumentTextIcon className="h-8 w-8 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Document Management</h1>
                  <p className="text-sm text-gray-600">Browse and manage documents across all your projects</p>
                </div>
              </div>
              <button
                onClick={handleUploadClick}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <DocumentArrowUpIcon className="-ml-1 mr-2 h-5 w-5" />
                Upload Documents
              </button>
            </div>
          </div>

          {/* Search and Filter Bar */}
          <div className="px-6 py-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search Input */}
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Project Filter */}
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Projects</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>

              {/* Status Filter */}
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="completed">Processed</option>
                <option value="failed">Failed</option>
              </select>

              {/* Clear Filters */}
              <button
                onClick={clearFilters}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Documents Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <button
            onClick={() => {/* Already showing all documents */}}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow text-left"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-600 truncate">Total Documents</dt>
                    <dd className="text-lg font-medium text-gray-900">{totalDocuments}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </button>

          <button
            onClick={() => setSelectedStatus('completed')}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow text-left"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-6 w-6 text-green-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-600 truncate">Processed</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {documents.filter(d => d.status === 'completed').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </button>

          <button
            onClick={() => setSelectedStatus('processing')}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow text-left"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ArrowPathIcon className="h-6 w-6 text-blue-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-600 truncate">Processing</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {documents.filter(d => d.status === 'processing').length}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </button>

          <button
            onClick={() => router.push('/projects')}
            className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow text-left"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <FolderOpenIcon className="h-6 w-6 text-blue-500" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-600 truncate">Projects</dt>
                    <dd className="text-lg font-medium text-gray-900">{projects.length}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </button>
      </div>

      {/* Documents List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Documents ({filteredDocuments.length})
            </h3>
          </div>

          {documentsLoading ? (
            <div className="p-6">
              <div className="animate-pulse space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-gray-200 rounded"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : filteredDocuments.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {filteredDocuments.map((document) => {
                const project = projects.find(p => p.id === document.project_id);
                
                return (
                  <div
                    key={document.id}
                    className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleDocumentClick(document)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                        <div>
                          <div className="flex items-center space-x-2">
                            <h4 className="text-lg font-medium text-gray-900">
                              {document.filename}
                            </h4>
                            {getStatusIcon(document.status)}
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                            <span>{document.filename}</span>
                            <span>•</span>
                            <span>{formatFileSize(document.file_size || 0)}</span>
                            <span>•</span>
                            <span className="flex items-center">
                              <FolderOpenIcon className="h-4 w-4 mr-1" />
                              {project?.name || 'Unknown Project'}
                            </span>
                            <span>•</span>
                            <span className="flex items-center">
                              <CalendarIcon className="h-4 w-4 mr-1" />
                              {new Date(document.created_at).toLocaleDateString()}
                            </span>
                            {document.chunk_count && (
                              <>
                                <span>•</span>
                                <span>{document.chunk_count} chunks</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(document.status)}`}>
                          {getStatusText(document.status)}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // View document details logic
                          }}
                          className="text-gray-400 hover:text-gray-600"
                          title="View document"
                        >
                          <EyeIcon className="h-5 w-5" />
                        </button>
                        <button
                          onClick={(e) => handleDeleteDocument(document.id, document.filename, e)}
                          className="text-red-600 hover:text-red-800 hover:bg-red-50 p-1 rounded transition-colors"
                          title="Delete document"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No documents found</h3>
              <p className="mt-1 text-sm text-gray-500">
                {searchTerm || selectedProject || selectedStatus
                  ? 'Try adjusting your search criteria or filters.'
                  : 'Upload your first document to get started with TinyRAG.'}
              </p>
              <div className="mt-6">
                <button
                  onClick={handleUploadClick}
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <DocumentArrowUpIcon className="-ml-1 mr-2 h-5 w-5" />
                  Upload Documents
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-6 rounded-lg shadow">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                <p className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span> to{' '}
                  <span className="font-medium">
                    {Math.min(currentPage * pageSize, totalDocuments)}
                  </span>{' '}
                  of <span className="font-medium">{totalDocuments}</span> results
                  </p>
                </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  {[...Array(Math.min(5, totalPages))].map((_, i) => {
                    const page = i + 1;
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          currentPage === page
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
} 