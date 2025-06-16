'use client';

import { useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface Document {
  id: string;
  title: string;
  status: 'processing' | 'ready' | 'error';
  createdAt: string;
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    onDrop: async (acceptedFiles) => {
      setIsUploading(true);
      try {
        // TODO: Implement file upload logic
        console.log('Files to upload:', acceptedFiles);
      } catch (error) {
        console.error('Upload failed:', error);
      } finally {
        setIsUploading(false);
      }
    }
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Documents</h1>
      
      {/* Upload Section */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}
      >
        <input {...getInputProps()} />
        {isUploading ? (
          <p className="text-gray-600">Uploading...</p>
        ) : isDragActive ? (
          <p className="text-blue-600">Drop the files here...</p>
        ) : (
          <p className="text-gray-600">
            Drag and drop files here, or click to select files
          </p>
        )}
        <p className="text-sm text-gray-500 mt-2">
          Supported formats: PDF, DOCX, PNG, JPG, TIFF (Max 50MB)
        </p>
      </div>

      {/* Documents List */}
      <div className="mt-8">
        {documents.length === 0 ? (
          <p className="text-center text-gray-500">No documents uploaded yet</p>
        ) : (
          <ul className="space-y-4">
            {documents.map((doc) => (
              <li
                key={doc.id}
                className="border rounded-lg p-4 flex items-center justify-between"
              >
                <div>
                  <h3 className="font-medium">{doc.title}</h3>
                  <p className="text-sm text-gray-500">
                    Uploaded on {new Date(doc.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm
                    ${doc.status === 'ready' ? 'bg-green-100 text-green-800' :
                      doc.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'}`}
                >
                  {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
} 