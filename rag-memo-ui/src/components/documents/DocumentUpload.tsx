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
      <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
      <p className="mt-2 text-sm text-gray-600">
        {isDragActive
          ? 'Drop the files here...'
          : 'Drag and drop PDF files here, or click to select files'}
      </p>
      <p className="mt-1 text-xs text-gray-500">
        Maximum file size: 10MB
      </p>
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