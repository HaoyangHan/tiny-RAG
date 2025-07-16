import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { DocumentIcon } from '@heroicons/react/24/outline';
import { documentApi } from '@/lib/api';
import { useDocumentStore } from '@/store';
import Button from '../ui/Button';
import toast from 'react-hot-toast';

export default function DocumentUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const addDocument = useDocumentStore((state) => state.addDocument);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    setIsUploading(true);
    try {
      for (const file of acceptedFiles) {
        const document = await documentApi.upload(file);
        addDocument(document);
        toast.success(`Successfully uploaded ${file.name}`);
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      toast.error('Failed to upload document');
    } finally {
      setIsUploading(false);
    }
  }, [addDocument]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400'
      }`}
    >
      <input {...getInputProps()} />
      <DocumentIcon className="mx-auto h-12 w-12 text-gray-500" />
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Select files
        </label>
        <div className="text-sm text-gray-600">
          <p className="text-sm text-gray-600 mt-2">
            Choose up to 10 files • PDF, TXT, DOCX supported • Max 50MB each
          </p>
        </div>
      </div>
      <Button
        variant="primary"
        size="sm"
        className="mt-4"
        isLoading={isUploading}
        disabled={isUploading}
      >
        {isUploading ? 'Uploading...' : 'Select Files'}
      </Button>
    </div>
  );
} 