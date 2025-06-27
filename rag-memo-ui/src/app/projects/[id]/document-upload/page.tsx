/**
 * Project-specific document upload page
 * Route: /projects/{id}/document-upload
 * TinyRAG v1.4.2 - Project-scoped document upload with ingestion status
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import {
  DocumentArrowUpIcon,
  ChevronLeftIcon,
  PlayIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { EnhancedDocumentUpload, DocumentUploadStatus } from '@/components/documents/EnhancedDocumentUpload';
import { api } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import { Project, Document } from '@/types';

interface ProjectDocumentUploadProps {
  params: { id: string };
}

// Document ingestion status mapping
const getIngestionStatusIcon = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
    case 'processing':
      return <ArrowPathIcon className="h-5 w-5 text-blue-600 animate-spin" />;
    case 'failed':
      return <ExclamationCircleIcon className="h-5 w-5 text-red-600" />;
    case 'pending':
    default:
      return <ClockIcon className="h-5 w-5 text-yellow-600" />;
  }
};

const getIngestionStatusText = (status: string) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return 'Ingested';
    case 'processing':
      return 'Processing';
    case 'failed':
      return 'Failed';
    case 'pending':
    default:
      return 'Pending';
  }
};

const getIngestionStatusColor = (status: string) => {
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

export default function ProjectDocumentUploadPage({ params }: ProjectDocumentUploadProps) {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [uploadedDocuments, setUploadedDocuments] = useState<DocumentUploadStatus[]>([]);
  const [isProcessingAll, setIsProcessingAll] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  // Fetch project data
  const { data: project, isLoading: projectLoading, error: projectError } = useQuery({
    queryKey: ['project', params.id],
    queryFn: () => api.getProject(params.id),
    enabled: isAuthenticated && !!params.id,
  });

  // Fetch project documents with real-time updates
  const { data: documentsData, isLoading: documentsLoading, refetch: refetchDocuments } = useQuery({
    queryKey: ['project-documents', params.id],
    queryFn: () => api.getDocuments({ project_id: params.id, page_size: 50 }),
    enabled: isAuthenticated && !!params.id,
    refetchInterval: 5000, // Refresh every 5 seconds to get updated ingestion status
  });

  const documents = documentsData?.items || [];

  const handleUploadComplete = (newDocuments: DocumentUploadStatus[]) => {
    setUploadedDocuments(newDocuments);
    // Refetch documents to show newly uploaded files
    refetchDocuments();
  };

  const handleUploadStart = (document: DocumentUploadStatus) => {
    console.log('Upload started for:', document.name);
  };

  const processAllDocuments = async () => {
    if (!project?.id) {
      alert('Project not found');
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
      const result = await api.executeAllElements(project.id);
      
      // Navigate to project elements page to monitor progress
      router.push(`/projects/${project.id}/elements?execution_id=${result.execution_id}`);
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
  const canProcessAll = completedUploads.length > 0;

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

  if (projectLoading) {
    return (
      <DashboardLayout title="Loading...">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-4 w-1/3"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (projectError || !project) {
    return (
      <DashboardLayout title="Error">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <ExclamationCircleIcon className="mx-auto h-12 w-12 text-red-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Project not found</h3>
            <p className="mt-1 text-sm text-gray-500">
              The project you're looking for doesn't exist or you don't have access to it.
            </p>
            <div className="mt-6">
              <button
                onClick={() => router.push('/projects')}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <ChevronLeftIcon className="-ml-1 mr-2 h-5 w-5" />
                Back to Projects
              </button>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`Upload Documents - ${project.name}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push(`/projects/${project.id}`)}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to {project.name}
          </button>
        </div>

        {/* Page Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <DocumentArrowUpIcon className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Upload Documents</h1>
                <p className="text-sm text-gray-600">
                  Add documents to <span className="font-medium">{project.name}</span> for AI processing
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Area */}
          <div className="space-y-6">
            {/* Enhanced Document Upload */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Documents</h3>
              <EnhancedDocumentUpload
                projectId={params.id}
                onUploadComplete={handleUploadComplete}
                onUploadStart={handleUploadStart}
                maxFiles={20}
                maxSizePerFile={100}
              />
            </div>

            {/* Process All Documents Button */}
            {canProcessAll && (
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Start Processing</h3>
                  <div className="flex items-center text-sm text-gray-500">
                    <InformationCircleIcon className="h-4 w-4 mr-1" />
                    {completedUploads.length} documents ready
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Begin AI processing to extract content and generate elements for the RAG pipeline.
                </p>
                <button
                  onClick={processAllDocuments}
                  disabled={isProcessingAll}
                  className="w-full flex items-center justify-center px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors"
                >
                  {isProcessingAll ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                      Starting Processing...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-4 w-4 mr-2" />
                      Start Processing All Documents
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
                    <p className="text-sm font-medium text-blue-900">AI Ingestion</p>
                    <p className="text-xs text-blue-700">Content is processed for RAG queries</p>
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

            {/* Project Documents with Ingestion Status */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Project Documents</h3>
              {documentsLoading ? (
                <div className="animate-pulse space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-200 rounded"></div>
                  ))}
                </div>
              ) : documents.length > 0 ? (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border"
                    >
                      <div className="flex items-center space-x-3">
                        <DocumentArrowUpIcon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                          <div className="flex items-center space-x-2 text-xs text-gray-500">
                            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                            {doc.file_size && (
                              <span>• {Math.round(doc.file_size / 1024)} KB</span>
                            )}
                            {doc.chunk_count && (
                              <span>• {doc.chunk_count} chunks</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getIngestionStatusIcon(doc.status)}
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getIngestionStatusColor(doc.status)}`}>
                          {getIngestionStatusText(doc.status)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <DocumentArrowUpIcon className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-500">No documents uploaded yet</p>
                  <p className="text-xs text-gray-400 mt-1">Upload your first document to get started</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 