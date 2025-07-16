/**
 * Enhanced Document Upload Component with Individual Status Tracking
 * TinyRAG v1.4.1 - Supports real-time upload progress and processing status
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  DocumentIcon, 
  TrashIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { api } from '@/services/api';

export interface DocumentUploadStatus {
  id: string;
  file: File;
  name: string;
  size: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
  documentId?: string;
  uploadedAt?: Date;
}

interface EnhancedDocumentUploadProps {
  projectId?: string;
  onUploadComplete?: (documents: DocumentUploadStatus[]) => void;
  onUploadStart?: (document: DocumentUploadStatus) => void;
  maxFiles?: number;
  maxSizePerFile?: number; // in MB
}

export function EnhancedDocumentUpload({ 
  projectId,
  onUploadComplete,
  onUploadStart,
  maxFiles = 10,
  maxSizePerFile = 50
}: EnhancedDocumentUploadProps) {
  const [documents, setDocuments] = useState<DocumentUploadStatus[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const abortControllersRef = useRef<Map<string, AbortController>>(new Map());

  const updateDocumentStatus = useCallback((id: string, updates: Partial<DocumentUploadStatus>) => {
    setDocuments(prev => prev.map(doc => 
      doc.id === id ? { ...doc, ...updates } : doc
    ));
  }, []);

  const uploadDocument = async (document: DocumentUploadStatus) => {
    const abortController = new AbortController();
    abortControllersRef.current.set(document.id, abortController);

    try {
      updateDocumentStatus(document.id, { status: 'uploading', progress: 0 });

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        updateDocumentStatus(document.id, { 
          progress: Math.min(document.progress + Math.random() * 20, 90) 
        });
      }, 500);

      // Upload document via API
      const uploadedDoc = await api.uploadDocument(document.file, projectId);
      
      clearInterval(progressInterval);
      
      updateDocumentStatus(document.id, {
        status: 'processing',
        progress: 95,
        documentId: uploadedDoc.id,
        uploadedAt: new Date()
      });

      // Simulate processing time
      setTimeout(() => {
        updateDocumentStatus(document.id, {
          status: 'completed',
          progress: 100
        });
      }, 2000);

    } catch (error: any) {
      console.error('Upload failed:', error);
      updateDocumentStatus(document.id, {
        status: 'failed',
        progress: 0,
        error: error.message || 'Upload failed'
      });
    } finally {
      abortControllersRef.current.delete(document.id);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[], rejectedFiles: any[]) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      console.warn('Some files were rejected:', rejectedFiles);
    }

    // Check file limits
    const totalFiles = documents.length + acceptedFiles.length;
    if (totalFiles > maxFiles) {
      alert(`Maximum ${maxFiles} files allowed. Please remove some files first.`);
      return;
    }

    // Create document status objects
    const newDocuments: DocumentUploadStatus[] = acceptedFiles.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file,
      name: file.name,
      size: file.size,
      status: 'pending',
      progress: 0
    }));

    // Add to documents list
    setDocuments(prev => [...prev, ...newDocuments]);
    setIsUploading(true);

    // Notify parent of upload start
    newDocuments.forEach(doc => onUploadStart?.(doc));

    // Upload documents sequentially
    for (const document of newDocuments) {
      await uploadDocument(document);
    }

    setIsUploading(false);
    
    // Notify parent of completion
    const updatedDocs = [...documents, ...newDocuments];
    onUploadComplete?.(updatedDocs);
  }, [documents, maxFiles, onUploadComplete, onUploadStart, projectId]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: true,
    maxSize: maxSizePerFile * 1024 * 1024, // Convert MB to bytes
    disabled: isUploading
  });

  const removeDocument = (id: string) => {
    // Cancel upload if in progress
    const abortController = abortControllersRef.current.get(id);
    if (abortController) {
      abortController.abort();
      abortControllersRef.current.delete(id);
    }

    // Remove from list
    setDocuments(prev => prev.filter(doc => doc.id !== id));
  };

  const retryUpload = async (id: string) => {
    const document = documents.find(doc => doc.id === id);
    if (document && document.status === 'failed') {
      await uploadDocument(document);
    }
  };

  const getStatusIcon = (status: DocumentUploadStatus['status']) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
      case 'uploading':
      case 'processing':
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <DocumentIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (doc: DocumentUploadStatus) => {
    switch (doc.status) {
      case 'pending':
        return 'Waiting to upload...';
      case 'uploading':
        return `Uploading... ${Math.round(doc.progress)}%`;
      case 'processing':
        return 'Processing document...';
      case 'completed':
        return 'Upload complete';
      case 'failed':
        return doc.error || 'Upload failed';
      default:
        return 'Unknown status';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>
        <div className="text-sm text-gray-600">
          {documents.length}/{maxFiles} files • Max {maxSizePerFile}MB per file
        </div>
      </div>
      
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : isUploading
            ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <DocumentIcon className="mx-auto h-12 w-12 text-gray-500" />
        <div className="mt-4">
          {isDragActive ? (
            <p className="text-blue-600">Drop the files here...</p>
          ) : isUploading ? (
            <p className="text-gray-600">Upload in progress...</p>
          ) : (
            <div>
              <p className="text-gray-600">
                Drag & drop documents here, or click to select
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Supports PDF, TXT, DOC, DOCX files
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Documents List */}
      {documents.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">
            Uploaded Documents ({documents.length})
          </h3>
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 shadow-sm"
              >
                <div className="flex items-center space-x-4 flex-1">
                  {getStatusIcon(doc.status)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {doc.name}
                      </p>
                      <p className="text-xs text-gray-600 ml-2">
                        {formatFileSize(doc.size)}
                      </p>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">
                      {getStatusText(doc)}
                    </p>
                    {/* Progress Bar */}
                    {(doc.status === 'uploading' || doc.status === 'processing') && (
                      <div className="mt-2">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${doc.progress}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  {doc.status === 'failed' && (
                    <button
                      onClick={() => retryUpload(doc.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      Retry
                    </button>
                  )}
                  <button
                    onClick={() => removeDocument(doc.id)}
                    className="text-red-600 hover:text-red-800"
                    disabled={doc.status === 'uploading'}
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 