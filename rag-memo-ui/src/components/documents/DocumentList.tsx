import { useEffect } from 'react';
import { DocumentIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useDocumentStore } from '@/store';
import { documentApi } from '@/lib/api';
import Button from '../ui/Button';
import toast from 'react-hot-toast';
import { Document } from '@/types';

export default function DocumentList() {
  const { documents, isLoading, error, setLoading, setError, removeDocument } = useDocumentStore();

  useEffect(() => {
    const fetchDocuments = async () => {
      setLoading(true);
      try {
        const fetchedDocuments = await documentApi.list();
        fetchedDocuments.forEach((doc: Document) => {
          useDocumentStore.getState().addDocument(doc);
        });
      } catch (error) {
        console.error('Error fetching documents:', error);
        setError('Failed to fetch documents');
        toast.error('Failed to fetch documents');
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [setLoading, setError]);

  const handleDelete = async (id: string) => {
    try {
      await documentApi.delete(id);
      removeDocument(id);
      toast.success('Document deleted successfully');
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('Failed to delete document');
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-500 p-4">
        <p>{error}</p>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center text-gray-500 p-4">
        <p>No documents uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-4 bg-white rounded-lg shadow"
        >
          <div className="flex items-center space-x-4">
            <DocumentIcon className="h-8 w-8 text-gray-400" />
            <div>
              <h3 className="text-sm font-medium text-gray-900">{doc.name}</h3>
              <p className="text-xs text-gray-500">
                {new Date(doc.createdAt).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span
              className={`px-2 py-1 text-xs rounded-full ${
                doc.status === 'completed'
                  ? 'bg-green-100 text-green-800'
                  : doc.status === 'processing'
                  ? 'bg-yellow-100 text-yellow-800'
                  : doc.status === 'failed'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {doc.status}
            </span>
            <Button
              variant="danger"
              size="sm"
              onClick={() => handleDelete(doc.id)}
              className="ml-2"
            >
              <TrashIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
} 