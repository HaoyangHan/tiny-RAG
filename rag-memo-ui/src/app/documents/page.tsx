/**
 * Documents page for uploading and listing documents.
 *
 * @returns {JSX.Element}
 */
'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  TrashIcon,
  PlayIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  CloudArrowUpIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

interface UploadedFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  error?: string;
}

export default function DocumentsPage() {
  const router = useRouter();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedProject, setSelectedProject] = useState('');
  const [isProcessingAll, setIsProcessingAll] = useState(false);

  // Mock projects - replace with actual API call
  const projects = [
    { id: '1', name: 'Customer Support Knowledge Base' },
    { id: '2', name: 'Product Documentation Assistant' },
  ];

  const supportedFormats = [
    { format: 'PDF', description: 'Adobe PDF documents', icon: '📄' },
    { format: 'DOCX', description: 'Microsoft Word documents', icon: '📝' },
    { format: 'TXT', description: 'Plain text files', icon: '📃' },
    { format: 'MD', description: 'Markdown files', icon: '📋' },
    { format: 'HTML', description: 'Web pages and HTML files', icon: '🌐' },
  ];

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFileSelection(files);
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    handleFileSelection(files);
  };

  const handleFileSelection = (files: File[]) => {
    const newFiles: UploadedFile[] = files.map((file, index) => ({
      id: `${Date.now()}-${index}`,
      file,
      status: 'pending',
      progress: 0,
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Auto-upload files
    newFiles.forEach(uploadedFile => {
      uploadFile(uploadedFile.id);
    });
  };

  const uploadFile = async (fileId: string) => {
    setUploadedFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, status: 'uploading' } : f
    ));

    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 100));
      setUploadedFiles(prev => prev.map(f => 
        f.id === fileId ? { ...f, progress } : f
      ));
    }

    setUploadedFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, status: 'completed', progress: 100 } : f
    ));
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const processAllDocuments = async () => {
    if (!selectedProject) {
      alert('Please select a project first');
      return;
    }

    setIsProcessingAll(true);
    
    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setIsProcessingAll(false);
    
    // Navigate to project elements page to trigger generation
    router.push(`/projects/${selectedProject}/elements`);
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      case 'uploading':
      case 'processing':
        return (
          <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full" />
        );
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status: UploadedFile['status']) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'uploading':
        return 'Uploading...';
      case 'processing':
        return 'Processing...';
      case 'completed':
        return 'Completed';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  const completedFiles = uploadedFiles.filter(f => f.status === 'completed');
  const canProcessAll = completedFiles.length > 0 && selectedProject;

  return (
    <DashboardLayout title="Document Upload">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Area */}
          <div className="space-y-6">
            {/* Project Selection */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Select Project</h3>
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
            </div>

            {/* File Drop Zone */}
            <div className="bg-white shadow rounded-lg p-6">
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  isDragging
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Upload Documents</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Drag and drop files here, or{' '}
                  <label className="text-blue-600 hover:text-blue-500 cursor-pointer">
                    browse
                    <input
                      type="file"
                      multiple
                      onChange={handleFileInput}
                      accept=".pdf,.docx,.txt,.md,.html"
                      className="hidden"
                    />
                  </label>
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  PDF, DOCX, TXT, MD, HTML up to 10MB each
                </p>
              </div>
            </div>

            {/* Upload Queue */}
            {uploadedFiles.length > 0 && (
              <div className="bg-white shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900">Upload Queue</h3>
                    <span className="text-sm text-gray-500">
                      {completedFiles.length} of {uploadedFiles.length} completed
                    </span>
                  </div>
                </div>
                <div className="divide-y divide-gray-200">
                  {uploadedFiles.map((uploadedFile) => (
                    <div key={uploadedFile.id} className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(uploadedFile.status)}
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {uploadedFile.file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB • {getStatusText(uploadedFile.status)}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => removeFile(uploadedFile.id)}
                          className="text-gray-400 hover:text-red-500"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                      {uploadedFile.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-200"
                              style={{ width: `${uploadedFile.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Batch Actions */}
            {completedFiles.length > 0 && (
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Process Documents</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Ready to process {completedFiles.length} documents and trigger element generation.
                </p>
                <button
                  onClick={processAllDocuments}
                  disabled={!canProcessAll || isProcessingAll}
                  className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    canProcessAll && !isProcessingAll
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-gray-400 cursor-not-allowed'
                  }`}
                >
                  {isProcessingAll ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-4 w-4 mr-2" />
                      Process All & Generate Elements
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Instructions & Info */}
          <div className="space-y-6">
            {/* Instructions */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Instructions</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-xs font-bold text-white">1</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Select Your Project</p>
                    <p className="text-sm text-gray-600">Choose which RAG project to upload documents to.</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-xs font-bold text-white">2</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Upload Documents</p>
                    <p className="text-sm text-gray-600">Drag and drop or browse to select your files.</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center mr-3 mt-0.5">
                    <span className="text-xs font-bold text-white">3</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">Process & Generate</p>
                    <p className="text-sm text-gray-600">Trigger document processing and element generation.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Supported Formats */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Supported Formats</h3>
              <div className="space-y-3">
                {supportedFormats.map((format) => (
                  <div key={format.format} className="flex items-center space-x-3">
                    <span className="text-2xl">{format.icon}</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{format.format}</p>
                      <p className="text-sm text-gray-600">{format.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Processing Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex">
                <InformationCircleIcon className="h-5 w-5 text-blue-400 mr-2 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <p className="font-medium">What happens next?</p>
                  <p className="mt-1">
                    After processing, your documents will be chunked, embedded, and indexed. 
                    You can then use them with your elements to generate intelligent responses.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 