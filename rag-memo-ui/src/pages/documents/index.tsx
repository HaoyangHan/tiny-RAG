import DocumentUpload from '@/components/documents/DocumentUpload';
import DocumentList from '@/components/documents/DocumentList';

export default function DocumentsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">Documents</h1>
        <div className="space-y-8">
          <DocumentUpload />
          <DocumentList />
        </div>
      </div>
    </div>
  );
} 