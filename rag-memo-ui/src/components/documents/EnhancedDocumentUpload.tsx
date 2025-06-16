/**
 * Enhanced Document Upload Component for TinyRAG v1.2
 * 
 * Supports multi-format document upload with drag-and-drop, preview, and progress tracking.
 * Includes support for PDF, DOCX, and image formats with OCR capabilities.
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Button from '../ui/Button';

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  preview?: string;
  error?: string;
}

interface EnhancedDocumentUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  maxFiles?: number;
  maxSize?: number;
  supportedFormats?: string[];
}

export function EnhancedDocumentUpload({
  onUpload,
  maxFiles = 10,
  maxSize = 50 * 1024 * 1024, // 50MB
  supportedFormats = ['pdf', 'docx', 'png', 'jpg', 'jpeg', 'tiff']
}: EnhancedDocumentUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setIsUploading(true);
    
    // Create file objects with initial state
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: 'uploading' as const,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    try {
      // Simulate upload progress
      for (const fileObj of newFiles) {
        // Update progress
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100));
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileObj.id 
                ? { ...f, progress, status: progress === 100 ? 'processing' : 'uploading' }
                : f
            )
          );
        }
      }

      // Call the upload handler
      await onUpload(acceptedFiles);

      // Mark as completed
      setUploadedFiles(prev => 
        prev.map(f => 
          newFiles.some(nf => nf.id === f.id)
            ? { ...f, status: 'completed' }
            : f
        )
      );
    } catch (error) {
      // Mark as error
      setUploadedFiles(prev => 
        prev.map(f => 
          newFiles.some(nf => nf.id === f.id)
            ? { ...f, status: 'error', error: error instanceof Error ? error.message : 'Upload failed' }
            : f
        )
      );
    } finally {
      setIsUploading(false);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff', '.tif']
    },
    maxFiles,
    maxSize,
    disabled: isUploading
  });

  const removeFile = (id: string) => {
    setUploadedFiles(prev => {
      const fileToRemove = prev.find(f => f.id === id);
      if (fileToRemove?.preview) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return prev.filter(f => f.id !== id);
    });
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'docx':
      case 'doc':
        return '📝';
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'tiff':
        return '🖼️';
      default:
        return '📎';
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
    <div className="w-full space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="text-6xl">📁</div>
          
          {isDragActive ? (
            <div>
              <p className="text-lg font-medium text-blue-600 dark:text-blue-400">
                Drop files here to upload
              </p>
              <p className="text-sm text-gray-500">
                Release to start processing
              </p>
            </div>
          ) : (
            <div>
              <p className="text-lg font-medium text-gray-900 dark:text-white">
                Drag & drop files here, or click to select
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supports PDF, DOCX, and images (PNG, JPG, TIFF) up to {formatFileSize(maxSize)}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Maximum {maxFiles} files at once
              </p>
            </div>
          )}

          <Button 
            variant="primary" 
            size="md"
            disabled={isUploading}
            className="mt-4"
          >
            {isUploading ? 'Uploading...' : 'Select Files'}
          </Button>
        </div>
      </div>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Uploaded Files ({uploadedFiles.length})
          </h3>
          
          <div className="space-y-2">
            {uploadedFiles.map((fileObj) => (
              <div
                key={fileObj.id}
                className="flex items-center space-x-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                {/* File Icon/Preview */}
                <div className="flex-shrink-0">
                  {fileObj.preview ? (
                    <img
                      src={fileObj.preview}
                      alt={fileObj.file.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  ) : (
                    <div className="w-12 h-12 flex items-center justify-center text-2xl">
                      {getFileIcon(fileObj.file.name)}
                    </div>
                  )}
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {fileObj.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(fileObj.file.size)}
                  </p>
                  
                  {/* Progress Bar */}
                  {fileObj.status === 'uploading' && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${fileObj.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Uploading... {fileObj.progress}%
                      </p>
                    </div>
                  )}

                  {/* Status */}
                  {fileObj.status === 'processing' && (
                    <p className="text-xs text-blue-600 mt-1">Processing...</p>
                  )}
                  
                  {fileObj.status === 'completed' && (
                    <p className="text-xs text-green-600 mt-1">✓ Upload complete</p>
                  )}
                  
                  {fileObj.status === 'error' && (
                    <p className="text-xs text-red-600 mt-1">
                      ✗ {fileObj.error || 'Upload failed'}
                    </p>
                  )}
                </div>

                {/* Remove Button */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(fileObj.id)}
                  className="text-gray-400 hover:text-red-600"
                >
                  ✕
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 