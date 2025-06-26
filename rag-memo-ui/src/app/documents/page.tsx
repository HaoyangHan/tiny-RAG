/**
 * Documents page for uploading and listing documents with real API integration.
 * TinyRAG v1.4.1 - Enhanced with individual document status tracking
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import {
  DocumentArrowUpIcon,
  PlayIcon,
  FolderPlusIcon,
  InformationCircleIcon,
  DocumentIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { EnhancedDocumentUpload, DocumentUploadStatus } from '@/components/documents/EnhancedDocumentUpload';
import { api } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

// Simple DocumentList component
function DocumentList({ documents }: { documents: any[] }) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusBadge = (status: string) => {
    const statusStyles: Record<string, string> = {
      'completed': 'bg-green-100 text-green-800',
      'processing': 'bg-yellow-100 text-yellow-800',
      'failed': 'bg-red-100 text-red-800',
      'pending': 'bg-gray-100 text-gray-800',
    };

    return (
      <span className={`px-2 py-1 text-xs rounded-full ${statusStyles[status] || statusStyles.pending}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div className="flex items-center space-x-3">
            <DocumentIcon className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">{doc.filename || doc.name}</p>
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <CalendarIcon className="h-3 w-3" />
                <span>{formatDate(doc.created_at || doc.createdAt)}</span>
                {doc.file_size && (
                  <span>• {Math.round(doc.file_size / 1024)} KB</span>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusBadge(doc.status || 'completed')}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DocumentsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [selectedProject, setSelectedProject] = useState('');
  const [isProcessingAll, setIsProcessingAll] = useState(false);
  const [uploadedDocuments, setUploadedDocuments] = useState<DocumentUploadStatus[]>([]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // Fetch projects for selection
  const { data: projectsData, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => api.getProjects({ page_size: 50 }),
    enabled: isAuthenticated,
  });

  // Fetch documents for selected project
  const { data: documentsData, isLoading: documentsLoading, refetch: refetchDocuments } = useQuery({
    queryKey: ['documents', selectedProject],
    queryFn: () => api.getDocuments({ project_id: selectedProject, page_size: 50 }),
    enabled: !!selectedProject,
  });

  const projects = projectsData?.items || [];
  const documents = documentsData?.items || [];

  const handleUploadComplete = (documents: DocumentUploadStatus[]) => {
    setUploadedDocuments(documents);
    // Refetch documents list to show newly uploaded documents
    if (selectedProject) {
      refetchDocuments();
    }
  };

  const handleUploadStart = (document: DocumentUploadStatus) => {
    console.log('Upload started for:', document.name);
  };

  const processAllDocuments = async () => {
    if (!selectedProject) {
      alert('Please select a project first');
      return;
    }

    const completedUploads = uploadedDocuments.filter(doc => doc.status === 'completed');
    if (completedUploads.length === 0) {
      alert('No completed uploads to process');
      return;
    }

    setIsProcessingAll(true);
    
    try {
      // Trigger all element execution for the project
      const result = await api.executeAllElements(selectedProject);
      
      // Navigate to project elements page to monitor progress
      router.push(`/projects/${selectedProject}/elements?execution_id=${result.execution_id}`);
    } catch (error: any) {
      console.error('Failed to process documents:', error);
      alert('Failed to start document processing. Please try again.');
    } finally {
      setIsProcessingAll(false);
    }
  };

  const supportedFormats = [
    { format: 'PDF', description: 'Adobe PDF documents', icon: '📄' },
    { format: 'DOCX', description: 'Microsoft Word documents', icon: '📝' },
    { format: 'TXT', description: 'Plain text files', icon: '📃' },
    { format: 'DOC', description: 'Microsoft Word legacy documents', icon: '📝' },
  ];

  const completedUploads = uploadedDocuments.filter(doc => doc.status === 'completed');
  const canProcessAll = completedUploads.length > 0 && selectedProject;

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
    <DashboardLayout title="Document Upload & Management">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Area */}
          <div className="space-y-6">
            {/* Project Selection */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Select Project</h3>
              {projectsLoading ? (
                <div className="animate-pulse">
                  <div className="h-10 bg-gray-200 rounded"></div>
                </div>
              ) : projects.length > 0 ? (
                <select
                  value={selectedProject}
                  onChange={(e) => setSelectedProject(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Choose a project to upload documents to</option>
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="text-center py-4">
                  <FolderPlusIcon className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-500 mb-3">No projects found</p>
                  <button
                    onClick={() => router.push('/projects/create')}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Create Project
                  </button>
                </div>
              )}
            </div>

            {/* Enhanced Document Upload */}
            {selectedProject && (
              <div className="bg-white shadow rounded-lg p-6">
                <EnhancedDocumentUpload
                  projectId={selectedProject}
                  onUploadComplete={handleUploadComplete}
                  onUploadStart={handleUploadStart}
                  maxFiles={20}
                  maxSizePerFile={100}
                />
              </div>
            )}

            {/* Process All Documents Button */}
            {canProcessAll && (
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Process Documents</h3>
                  <div className="flex items-center text-sm text-gray-500">
                    <InformationCircleIcon className="h-4 w-4 mr-1" />
                    {completedUploads.length} documents ready
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Generate all elements for the uploaded documents to start the RAG pipeline.
                </p>
                <button
                  onClick={processAllDocuments}
                  disabled={isProcessingAll}
                  className="w-full flex items-center justify-center px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
                >
                  {isProcessingAll ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-4 w-4 mr-2" />
                      Process All Documents
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Information & Document List */}
          <div className="space-y-6">
            {/* Supported Formats */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Supported Formats</h3>
              <div className="grid grid-cols-1 gap-3">
                {supportedFormats.map((format) => (
                  <div key={format.format} className="flex items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-2xl mr-3">{format.icon}</span>
                    <div>
                      <div className="font-medium text-gray-900">{format.format}</div>
                      <div className="text-sm text-gray-500">{format.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Processing Pipeline Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-4">Processing Pipeline</h3>
              <div className="space-y-3">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-xs font-bold text-white">1</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Document Upload</p>
                    <p className="text-xs text-blue-700">Files are uploaded and validated</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-xs font-bold text-white">2</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Content Extraction</p>
                    <p className="text-xs text-blue-700">Text and metadata are extracted</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-xs font-bold text-white">3</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Element Generation</p>
                    <p className="text-xs text-blue-700">AI elements process the content</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-xs font-bold text-white">4</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-blue-900">Ready for Queries</p>
                    <p className="text-xs text-blue-700">Documents are ready for Q&A</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Existing Documents List */}
            {selectedProject && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Project Documents</h3>
                {documentsLoading ? (
                  <div className="animate-pulse space-y-3">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="h-12 bg-gray-200 rounded"></div>
                    ))}
                  </div>
                ) : documents.length > 0 ? (
                  <DocumentList documents={documents} />
                ) : (
                  <div className="text-center py-8">
                    <DocumentArrowUpIcon className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-500">No documents uploaded yet</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 