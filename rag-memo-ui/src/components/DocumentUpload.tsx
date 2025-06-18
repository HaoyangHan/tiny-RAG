'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { DocumentIcon, TrashIcon } from '@heroicons/react/24/outline';

interface DocumentUploadProps {
  onUpload: (fileName: string) => void;
  uploadedDocuments: string[];
}

export function DocumentUpload({ onUpload, uploadedDocuments }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true);
    
    for (const file of acceptedFiles) {
      try {
        // Mock upload - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        onUpload(file.name);
      } catch (error) {
        console.error('Upload failed:', error);
      }
    }
    
    setIsUploading(false);
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: true
  });

  const removeDocument = (fileName: string) => {
    // This would typically call an API to remove the document
    console.log('Remove document:', fileName);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>
      
      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          {isDragActive ? (
            <p className="text-blue-600">Drop the files here...</p>
          ) : (
            <div>
              <p className="text-gray-600">
                Drag & drop documents here, or click to select
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supports PDF, TXT, DOC, DOCX files
              </p>
            </div>
          )}
        </div>
        {isUploading && (
          <div className="mt-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-sm text-gray-600 mt-2">Uploading...</p>
          </div>
        )}
      </div>

      {/* Uploaded Documents List */}
      {uploadedDocuments.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-lg font-medium text-gray-900">
            Uploaded Documents ({uploadedDocuments.length})
          </h3>
          <div className="space-y-2">
            {uploadedDocuments.map((fileName, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200"
              >
                <div className="flex items-center space-x-3">
                  <DocumentIcon className="h-5 w-5 text-gray-400" />
                  <span className="text-sm text-gray-900">{fileName}</span>
                </div>
                <button
                  onClick={() => removeDocument(fileName)}
                  className="text-red-600 hover:text-red-800"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 