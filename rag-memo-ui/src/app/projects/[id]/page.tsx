'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import {
  ChevronLeftIcon,
  DocumentTextIcon,
  CpuChipIcon,
  SparklesIcon,
  Cog6ToothIcon,
  EyeIcon,
  UsersIcon,
  CalendarIcon,
  ChartBarIcon,
  PlusIcon,
  FolderOpenIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  ExclamationCircleIcon,
  ClockIcon,
  ChevronLeftIcon as ChevronLeftPageIcon,
  ChevronRightIcon as ChevronRightPageIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  PencilIcon,
  XMarkIcon,
  HashtagIcon,
  DocumentDuplicateIcon,
  PlayIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Project, TenantType, ProjectStatus, Document, Element, Generation, ElementType, ElementStatus } from '@/types';
import { api } from '@/services/api';

interface ProjectDetailsProps {
  params: { id: string };
}

export default function ProjectDetailsPage({ params }: ProjectDetailsProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');
  
  // State for project data
  const [project, setProject] = useState<Project | null>(null);
  const [recentDocuments, setRecentDocuments] = useState<Document[]>([]);
  const [recentElements, setRecentElements] = useState<Element[]>([]);
  const [recentGenerations, setRecentGenerations] = useState<Generation[]>([]);
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);  


  // Documents tab pagination state
  const [documentsPage, setDocumentsPage] = useState(1);
  const documentsPageSize = 20;
  
  // Elements tab pagination state
  const [elementsPage, setElementsPage] = useState(1);
  const elementsPageSize = 20;

  // Generations tab pagination state
  const [generationsPage, setGenerationsPage] = useState(1);
  const generationsPageSize = 20;
  const [allGenerations, setAllGenerations] = useState<Generation[]>([]);
  const [totalGenerations, setTotalGenerations] = useState(0);
  const [isLoadingGenerations, setIsLoadingGenerations] = useState(false);

  // Expansion state for documents and elements
  const [expandedDocuments, setExpandedDocuments] = useState<Set<string>>(new Set());
  const [expandedElements, setExpandedElements] = useState<Set<string>>(new Set());
  const [editingElements, setEditingElements] = useState<Set<string>>(new Set());
  
  // Document and Element detail data
  const [documentDetails, setDocumentDetails] = useState<Map<string, any>>(new Map());
  const [elementDetails, setElementDetails] = useState<Map<string, any>>(new Map());
  const [elementEditData, setElementEditData] = useState<Map<string, any>>(new Map());
  const [deletingDocument, setDeletingDocument] = useState<string | null>(null);
  
  // Element generation state
  const [isGeneratingElements, setIsGeneratingElements] = useState(false);

  // Tab definitions
  const tabs = [
    { id: 'overview', name: 'Overview', icon: FolderOpenIcon },
    { id: 'documents', name: 'Documents', icon: DocumentTextIcon },
    { id: 'elements', name: 'Elements', icon: CpuChipIcon },
    { id: 'generations', name: 'Generations', icon: SparklesIcon },
    { id: 'settings', name: 'Settings', icon: Cog6ToothIcon },
  ];

  // Function to toggle document expansion and fetch details
  const toggleDocumentExpansion = async (documentId: string) => {
    const newExpanded = new Set(expandedDocuments);
    
    if (expandedDocuments.has(documentId)) {
      newExpanded.delete(documentId);
    } else {
      newExpanded.add(documentId);
      
      // Fetch document details if not already loaded
      if (!documentDetails.has(documentId)) {
        try {
          const details = await api.getDocument(documentId);
          setDocumentDetails(new Map(documentDetails.set(documentId, details)));
        } catch (error) {
          console.error('Failed to fetch document details:', error);
        }
      }
    }
    
    setExpandedDocuments(newExpanded);
  };

  // Function to toggle element expansion and fetch details
  const toggleElementExpansion = async (elementId: string) => {
    const newExpanded = new Set(expandedElements);
    
    if (expandedElements.has(elementId)) {
      newExpanded.delete(elementId);
    } else {
      newExpanded.add(elementId);
      
      // Fetch element details if not already loaded
      if (!elementDetails.has(elementId)) {
        try {
          const details = await api.getElement(elementId);
          setElementDetails(new Map(elementDetails.set(elementId, details)));
        } catch (error) {
          console.error('Failed to fetch element details:', error);
        }
      }
    }
    
    setExpandedElements(newExpanded);
  };

  // Function to start editing an element
  const startElementEdit = (elementId: string) => {
    const element = elementDetails.get(elementId);
    if (element) {
      setElementEditData(new Map(elementEditData.set(elementId, {
        name: element.name,
        description: element.description || '',
        template_content: element.template?.content || element.template_content || '',
        variables: element.template?.variables || element.template_variables || [],
        tags: element.tags || []
      })));
      setEditingElements(new Set(editingElements.add(elementId)));
    }
  };

  // Function to cancel element editing
  const cancelElementEdit = (elementId: string) => {
    const newEditing = new Set(editingElements);
    newEditing.delete(elementId);
    setEditingElements(newEditing);
    
    const newEditData = new Map(elementEditData);
    newEditData.delete(elementId);
    setElementEditData(newEditData);
  };

  // Function to save element changes
  const saveElementChanges = async (elementId: string) => {
    const editData = elementEditData.get(elementId);
    if (!editData) return;

    try {
      // TODO: Implement updateElement API method
      // For now, just update the local state
      const currentElement = elementDetails.get(elementId);
      const updatedElement = { ...currentElement, ...editData };
      
      // Update the element details cache
      setElementDetails(new Map(elementDetails.set(elementId, updatedElement)));
      
      // Exit edit mode
      cancelElementEdit(elementId);
      
      // Show success message
      alert('Element updated successfully! (Note: Changes are local only until API is implemented)');
      
    } catch (error) {
      console.error('Failed to save element changes:', error);
      alert('Failed to save changes. Please try again.');
    }
  };

  // Function to update element edit data
  const updateElementEditData = (elementId: string, field: string, value: any) => {
    const currentData = elementEditData.get(elementId) || {};
    const newData = { ...currentData, [field]: value };
    setElementEditData(new Map(elementEditData.set(elementId, newData)));
  };

  // Function to handle document deletion
  const handleDeleteDocument = async (documentId: string, filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingDocument(documentId);
      
      // Call delete API
      await api.deleteDocument(documentId);
      
      // Remove from local state
      setRecentDocuments((docs: Document[]) => docs.filter((doc: Document) => doc.id !== documentId));
      
      // Refetch documents if we're on the documents tab
      if (activeTab === 'documents' && refetchAllDocuments) {
        refetchAllDocuments();
      }
      
      // Remove from expanded documents
      const newExpanded = new Set(expandedDocuments);
      newExpanded.delete(documentId);
      setExpandedDocuments(newExpanded);
      
      // Remove from document details cache
      const newDetails = new Map(documentDetails);
      newDetails.delete(documentId);
      setDocumentDetails(newDetails);
      
      // Show success message
      alert(`Document "${filename}" deleted successfully!`);
      
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert(`Failed to delete document "${filename}". Please try again.`);
    } finally {
      setDeletingDocument(null);
    }
  };

  // Function to handle "Generate All Elements" action
  const handleGenerateAllElements = async () => {
    if (!project?.id) {
      alert('Project not found');
      return;
    }

    const completedDocuments = allDocuments.filter(doc => doc.status === 'completed');
    if (completedDocuments.length === 0) {
      alert('No completed documents found. Please ensure all documents are processed before generating elements.');
      return;
    }

    setIsGeneratingElements(true);
    
    try {
      // Call the bulk element execution API
      const result = await api.executeAllElements(project.id);
      
      // Redirect to the generations page to monitor progress
      router.push(`/generations?project_id=${project.id}&execution_id=${result.execution_id}`);
      
    } catch (error: any) {
      console.error('Failed to generate elements:', error);
      alert('Failed to start element generation. Please try again.');
      setIsGeneratingElements(false);
    }
  };

  // Function to fetch generations for the project
  const fetchGenerations = async (page: number = 1) => {
    if (!project?.id) return;
    
    try {
      setIsLoadingGenerations(true);
      console.log('Fetching generations for project:', project.id, 'page:', page);
      
      const response = await api.getGenerations({
        project_id: project.id,
        page: page,
        page_size: generationsPageSize,
        include_content: true
      });
      
      console.log('Generations response:', response);
      setAllGenerations(response.items || []);
      setTotalGenerations(response.total_count || 0);
      setGenerationsPage(page);
      
    } catch (error) {
      console.error('Failed to fetch generations:', error);
      // Set empty state on error to prevent showing stale data
      setAllGenerations([]);
      setTotalGenerations(0);
    } finally {
      setIsLoadingGenerations(false);
    }
  };

  // Fetch project data on component mount
  useEffect(() => {
    const fetchProjectData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        console.log('=== DEBUGGING PROJECT DATA FETCH ===');
        console.log('Project ID:', params.id);
        
        // Test API client health and authentication
        try {
          const healthCheck = await api.checkHealth();
          console.log('API Health check:', healthCheck);
        } catch (healthError) {
          console.error('API Health check failed:', healthError);
        }
        
        // Test if API client has token
        console.log('API client token status:', (api as any).token ? 'Token exists' : 'No token');

        // Fetch project details
        const projectData = await api.getProject(params.id);
        console.log('Project data fetched:', projectData);
        setProject(projectData);

        // Fetch related data in parallel (only recent items for overview)
        console.log('Fetching parallel data...');
        const [documentsResponse, elementsResponse, generationsResponse] = await Promise.allSettled([
          api.getDocuments({ project_id: params.id, page_size: 5 }),
          api.getElements({ project_id: params.id, page_size: 5 }),
          api.getGenerations({ project_id: params.id, page_size: 5, include_content: true })
        ]);

        console.log('Documents response:', documentsResponse);
        console.log('Elements response:', elementsResponse);
        console.log('Generations response:', generationsResponse);

        // Handle documents response
        if (documentsResponse.status === 'fulfilled') {
          console.log('Documents data:', documentsResponse.value);
          setRecentDocuments(documentsResponse.value.items || []);
        } else {
          console.error('Documents fetch failed:', documentsResponse.reason);
        }

        // Handle elements response
        if (elementsResponse.status === 'fulfilled') {
          console.log('Elements data:', elementsResponse.value);
          setRecentElements(elementsResponse.value.items || []);
        } else {
          console.error('Elements fetch failed:', elementsResponse.reason);
        }

        // Handle generations response
        if (generationsResponse.status === 'fulfilled') {
          console.log('Generations data:', generationsResponse.value);
          console.log('Total generations count:', generationsResponse.value.total_count);
          setRecentGenerations(generationsResponse.value.items || []);
          // Also set total count for overview display
          setTotalGenerations(generationsResponse.value.total_count || 0);
        } else {
          console.error('Generations fetch failed:', generationsResponse.reason);
        }

        console.log('=== END DEBUGGING ===');

      } catch (err) {
        console.error('Failed to fetch project data:', err);
        setError('Failed to load project data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (params.id) {
      fetchProjectData();
    }
  }, [params.id]);

  // Separate query for full documents list in Documents tab
  const { data: allDocumentsData, isLoading: allDocumentsLoading, refetch: refetchAllDocuments } = useQuery({
    queryKey: ['project-all-documents', params.id, documentsPage],
    queryFn: () => api.getDocuments({ 
      project_id: params.id, 
      page: documentsPage,
      page_size: documentsPageSize 
    }),
    enabled: !!params.id && activeTab === 'documents',
    refetchInterval: 5000, // Real-time updates for document status
  });

  const allDocuments = allDocumentsData?.items || [];
  const totalDocuments = allDocumentsData?.total_count || 0;
  const totalDocumentPages = Math.ceil(totalDocuments / documentsPageSize);

  // Separate query for full elements list in Elements tab
  const { data: allElementsData, isLoading: allElementsLoading, refetch: refetchAllElements } = useQuery({
    queryKey: ['project-all-elements', params.id, elementsPage],
    queryFn: () => api.getElements({ 
      project_id: params.id, 
      page: elementsPage,
      page_size: elementsPageSize 
    }),
    enabled: !!params.id && activeTab === 'elements',
  });

  const allElements = allElementsData?.items || [];
  const totalElements = allElementsData?.total_count || 0;
  const totalElementPages = Math.ceil(totalElements / elementsPageSize);

  // Calculate generations pagination
  const totalGenerationPages = Math.ceil(totalGenerations / generationsPageSize);

  // Use real generation count instead of potentially stale project.generation_count
  const realGenerationCount = totalGenerations || recentGenerations.length || 0;
  
  // Debug logging
  console.log('Current state - totalGenerations:', totalGenerations, 'recentGenerations.length:', recentGenerations.length, 'realGenerationCount:', realGenerationCount);

  // Add useEffect to fetch generations when Generations tab is activated
  useEffect(() => {
    if (activeTab === 'generations' && project?.id) {
      fetchGenerations(1);
    }
  }, [activeTab, project?.id]);

  // Show loading spinner while fetching data
  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  // Show error message if failed to load
  if (error || !project) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {error || 'Project not found'}
            </h2>
            <button
              onClick={() => router.push('/projects')}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <ChevronLeftIcon className="h-5 w-5 mr-2" />
              Back to Projects
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // Helper function to get tenant type display name
  const getTenantTypeDisplay = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'hr':
        return 'Human Resources';
      case 'coding':
        return 'Software Development';
      case 'financial_report':
        return 'Financial Analysis';
      case 'deep_research':
        return 'Research & Analysis';
      case 'qa_generation':
        return 'Q&A Generation';
      case 'raw_rag':
        return 'General RAG Tasks';
      default:
        return type || 'Unknown';
    }
  };

  // Helper function to format dates
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Helper function to get ingestion status icon
  const getIngestionStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'processed':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'processing':
      case 'uploading':
        return <ArrowPathIcon className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'failed':
      case 'error':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-600" />;
      case 'pending':
      default:
        return <ClockIcon className="h-5 w-5 text-yellow-600" />;
    }
  };

  // Helper function to get status badge color
  const getStatusBadgeColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'processed':
        return 'bg-green-100 text-green-800';
      case 'processing':
      case 'uploading':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'pending':
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  // Project overview render function
  const renderProjectOverview = () => (
    <div className="space-y-6">
      {/* Project Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Documents</p>
                <button
                  onClick={() => setActiveTab('documents')}
                  className="text-2xl font-semibold text-gray-900 hover:text-blue-600 transition-colors duration-200 cursor-pointer"
                >
                  {project.document_count}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CpuChipIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Elements</p>
                <button
                  onClick={() => setActiveTab('elements')}
                  className="text-2xl font-semibold text-gray-900 hover:text-green-600 transition-colors duration-200 cursor-pointer"
                >
                  {project.element_count}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <SparklesIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Generations</p>
                <button
                  onClick={() => setActiveTab('generations')}
                  className="text-2xl font-semibold text-gray-900 hover:text-purple-600 transition-colors duration-200 cursor-pointer"
                >
                  {realGenerationCount}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UsersIcon className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500">Team Members</p>
                <p className="text-2xl font-semibold text-gray-900">{project.collaborators.length + 1}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Recent Documents</h3>
              <button
                onClick={() => setActiveTab('documents')}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                View all
              </button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentDocuments.map((doc) => (
              <div key={doc.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <DocumentTextIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                      <p className="text-xs text-gray-500">
                        {(doc.file_size / 1024).toFixed(1)} KB • {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Processed
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Elements */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Recent Elements</h3>
              <button
                onClick={() => setActiveTab('elements')}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                View all
              </button>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {recentElements.map((element) => (
              <div key={element.id} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <CpuChipIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{element.name}</p>
                      <p className="text-xs text-gray-500">
                        {element.execution_count} executions • Last run Never
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Project Description */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">About This Project</h3>
        <p className="text-gray-600 mb-4">{project.description}</p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-sm font-medium text-gray-500">Keywords</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {project.keywords.map((keyword) => (
                <span
                  key={keyword}
                  className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-blue-100 text-blue-800"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Created</p>
            <p className="text-sm text-gray-900 mt-1">
              {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Last Updated</p>
            <p className="text-sm text-gray-900 mt-1">
              {new Date(project.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  // Project documents render function with expandable details
  const renderProjectDocuments = () => {
    // Check if all documents are completed for enabling "Generate All Elements" button
    const completedDocuments = allDocuments.filter(doc => doc.status === 'completed');
    const allDocumentsCompleted = allDocuments.length > 0 && completedDocuments.length === allDocuments.length;
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Project Documents</h3>
            <p className="text-sm text-gray-500 mt-1">
              {totalDocuments} total documents • {completedDocuments.length} completed • Real-time status updates
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {/* Generate All Elements Button */}
            {allDocuments.length > 0 && (
              <button
                onClick={handleGenerateAllElements}
                disabled={!allDocumentsCompleted || isGeneratingElements}
                className={`inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md transition-colors ${
                  allDocumentsCompleted && !isGeneratingElements
                    ? 'text-white bg-green-600 hover:bg-green-700'
                    : 'text-gray-400 bg-gray-200 cursor-not-allowed'
                }`}
                title={!allDocumentsCompleted ? 'All documents must be completed before generating elements' : 'Generate content for all project elements'}
              >
                {isGeneratingElements ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    <CpuChipIcon className="-ml-1 mr-2 h-5 w-5" />
                    Generate All Elements
                  </>
                )}
              </button>
            )}
            
            {/* Upload Documents Button */}
            <button
              onClick={() => router.push(`/projects/${project.id}/document-upload`)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
              Upload Documents
            </button>
          </div>
        </div>

      {allDocumentsLoading ? (
        <div className="flex justify-center py-8">
          <LoadingSpinner size="md" />
        </div>
      ) : allDocuments.length > 0 ? (
        <>
          <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
            {allDocuments.map((doc) => (
              <div key={doc.id} className="overflow-hidden">
                {/* Main document card */}
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="text-lg font-medium text-gray-900">{doc.filename}</h4>
                          <CheckCircleIcon className="h-5 w-5 text-green-600" />
                        </div>
                        <p className="text-sm text-gray-500">
                          {doc.content_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Uploaded {new Date(doc.created_at).toLocaleDateString()} • {doc.chunk_count || 0} chunks
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {doc.status}
                      </span>
                      <button
                        onClick={() => toggleDocumentExpansion(doc.id)}
                        className="text-gray-400 hover:text-gray-600 p-1"
                      >
                        {expandedDocuments.has(doc.id) ? (
                          <ChevronDownIcon className="h-5 w-5" />
                        ) : (
                          <ChevronRightIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expanded document details */}
                {expandedDocuments.has(doc.id) && (
                  <div className="border-t border-gray-200 bg-gray-50">
                    <div className="p-6">
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Document Metadata */}
                        <div>
                          <h5 className="text-sm font-medium text-gray-900 mb-3">Document Information</h5>
                          <dl className="space-y-2">
                            <div className="flex justify-between">
                              <dt className="text-sm text-gray-500">File Size</dt>
                              <dd className="text-sm text-gray-900">{(doc.file_size / 1024).toFixed(1)} KB</dd>
                            </div>
                            <div className="flex justify-between">
                              <dt className="text-sm text-gray-500">Content Type</dt>
                              <dd className="text-sm text-gray-900">{doc.content_type}</dd>
                            </div>
                            <div className="flex justify-between">
                              <dt className="text-sm text-gray-500">Chunks</dt>
                              <dd className="text-sm text-gray-900">{doc.chunk_count || 0}</dd>
                            </div>
                            <div className="flex justify-between">
                              <dt className="text-sm text-gray-500">Status</dt>
                              <dd className="text-sm text-gray-900">{doc.status}</dd>
                            </div>
                            <div className="flex justify-between">
                              <dt className="text-sm text-gray-500">Created</dt>
                              <dd className="text-sm text-gray-900">{formatDate(doc.created_at)}</dd>
                            </div>
                          </dl>
                        </div>

                        {/* Chunk Information */}
                        <div>
                          <h5 className="text-sm font-medium text-gray-900 mb-3">Chunk Analysis</h5>
                          <div className="space-y-2">
                            <div className="flex items-center justify-between p-3 bg-white rounded-md border border-gray-200">
                              <div className="flex items-center space-x-2">
                                <HashtagIcon className="h-4 w-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Total Chunks</span>
                              </div>
                              <span className="text-sm font-medium text-gray-900">{doc.chunk_count || 0}</span>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-white rounded-md border border-gray-200">
                              <div className="flex items-center space-x-2">
                                <DocumentDuplicateIcon className="h-4 w-4 text-gray-400" />
                                <span className="text-sm text-gray-600">Avg. Chunk Size</span>
                              </div>
                              <span className="text-sm font-medium text-gray-900">
                                {doc.chunk_count ? Math.round(doc.file_size / doc.chunk_count) : 0} bytes
                              </span>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-white rounded-md border border-gray-200">
                              <div className="flex items-center space-x-2">
                                <CheckCircleIcon className="h-4 w-4 text-green-500" />
                                <span className="text-sm text-gray-600">Processing</span>
                              </div>
                              <span className="text-sm font-medium text-green-600">Completed</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Document Metadata Tags */}
                      {doc.metadata && Object.keys(doc.metadata).length > 0 && (
                        <div className="mt-6">
                          <h5 className="text-sm font-medium text-gray-900 mb-3">Document Metadata</h5>
                          <div className="flex flex-wrap gap-2">
                            {Object.entries(doc.metadata).map(([key, value]) => (
                              <span
                                key={key}
                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {key}: {String(value)}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="mt-6 flex space-x-3">
                        <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50">
                          <EyeIcon className="h-4 w-4 mr-2" />
                          View Content
                        </button>
                        <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50">
                          <DocumentDuplicateIcon className="h-4 w-4 mr-2" />
                          View Chunks
                        </button>
                        <button
                          onClick={() => handleDeleteDocument(doc.id, doc.filename)}
                          disabled={deletingDocument === doc.id}
                          className="inline-flex items-center px-3 py-2 border border-red-300 rounded-md text-red-700 bg-white hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <TrashIcon className="h-4 w-4 mr-2" />
                          {deletingDocument === doc.id ? 'Deleting...' : 'Delete'}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalDocumentPages > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-lg">
              <div className="flex flex-1 justify-between sm:hidden">
                <button
                  onClick={() => setDocumentsPage(Math.max(1, documentsPage - 1))}
                  disabled={documentsPage === 1}
                  className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setDocumentsPage(Math.min(totalDocumentPages, documentsPage + 1))}
                  disabled={documentsPage === totalDocumentPages}
                  className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
              <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing{' '}
                    <span className="font-medium">{(documentsPage - 1) * documentsPageSize + 1}</span>
                    {' '}to{' '}
                    <span className="font-medium">
                      {Math.min(documentsPage * documentsPageSize, totalDocuments)}
                    </span>
                    {' '}of{' '}
                    <span className="font-medium">{totalDocuments}</span>
                    {' '}results
                  </p>
                </div>
                <div>
                  <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                    <button
                      onClick={() => setDocumentsPage(Math.max(1, documentsPage - 1))}
                      disabled={documentsPage === 1}
                      className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                    >
                      <ChevronLeftPageIcon className="h-5 w-5" aria-hidden="true" />
                    </button>
                    <span className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300">
                      {documentsPage} of {totalDocumentPages}
                    </span>
                    <button
                      onClick={() => setDocumentsPage(Math.min(totalDocumentPages, documentsPage + 1))}
                      disabled={documentsPage === totalDocumentPages}
                      className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                    >
                      <ChevronRightPageIcon className="h-5 w-5" aria-hidden="true" />
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No documents</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by uploading your first document to this project.
          </p>
          <div className="mt-6">
            <button
              onClick={() => router.push(`/projects/${project.id}/document-upload`)}
              className="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
            >
              <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
              Upload Document
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

  // Project elements render function with expandable details and editing
  const renderProjectElements = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Project Elements</h3>
        <button
          onClick={() => router.push('/elements/create')}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
          Create Element
        </button>
      </div>

      {allElementsLoading ? (
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner size="md" />
        </div>
      ) : allElements.length === 0 ? (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="text-center">
            <CpuChipIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No elements found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first element.
            </p>
            <div className="mt-6">
              <button
                onClick={() => router.push('/elements/create')}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                Create Element
              </button>
            </div>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
            {allElements.map((element) => (
              <div key={element.id} className="overflow-hidden">
                {/* Main element card */}
                <div className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 flex-1">
                      <CpuChipIcon className="h-8 w-8 text-gray-400" />
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => router.push(`/elements/${element.id}`)}
                            className="text-lg font-medium text-gray-900 hover:text-blue-600 transition-colors duration-200"
                          >
                            {element.name}
                          </button>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            element.element_type === ElementType.PROMPT_TEMPLATE ? 'bg-blue-100 text-blue-800' :
                            element.element_type === ElementType.AGENTIC_TOOL ? 'bg-green-100 text-green-800' :
                            element.element_type === ElementType.MCP_CONFIG ? 'bg-purple-100 text-purple-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {element.element_type.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500">{element.description}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {element.execution_count} executions • Last updated {formatDate(element.updated_at)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        element.status === ElementStatus.ACTIVE ? 'bg-green-100 text-green-800' :
                        element.status === ElementStatus.DRAFT ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {element.status}
                      </span>
                      <button
                        onClick={() => toggleElementExpansion(element.id)}
                        className="text-gray-400 hover:text-gray-600 p-1"
                      >
                        {expandedElements.has(element.id) ? (
                          <ChevronDownIcon className="h-5 w-5" />
                        ) : (
                          <ChevronRightIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expanded element details */}
                {expandedElements.has(element.id) && (
                  <div className="border-t border-gray-200 bg-gray-50">
                    <div className="p-6">
                      {editingElements.has(element.id) ? (
                        /* Edit Mode */
                        <div className="space-y-6">
                          <div className="flex items-center justify-between">
                            <h5 className="text-sm font-medium text-gray-900">Edit Element</h5>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => saveElementChanges(element.id)}
                                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                              >
                                <CheckCircleIcon className="h-4 w-4 mr-2" />
                                Save
                              </button>
                              <button
                                onClick={() => cancelElementEdit(element.id)}
                                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                              >
                                <XMarkIcon className="h-4 w-4 mr-2" />
                                Cancel
                              </button>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Basic Information */}
                            <div className="space-y-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                  Element Name
                                </label>
                                <input
                                  type="text"
                                  value={elementEditData.get(element.id)?.name || ''}
                                  onChange={(e) => updateElementEditData(element.id, 'name', e.target.value)}
                                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                                />
                              </div>
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                  Description
                                </label>
                                <textarea
                                  rows={3}
                                  value={elementEditData.get(element.id)?.description || ''}
                                  onChange={(e) => updateElementEditData(element.id, 'description', e.target.value)}
                                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                                />
                              </div>
                            </div>

                            {/* Template Content */}
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Template Content
                              </label>
                              <textarea
                                rows={8}
                                value={elementEditData.get(element.id)?.template_content || ''}
                                onChange={(e) => updateElementEditData(element.id, 'template_content', e.target.value)}
                                className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-gray-900"
                              />
                            </div>
                          </div>
                        </div>
                      ) : (
                        /* View Mode */
                        <div className="space-y-6">
                          <div className="flex items-center justify-between">
                            <h5 className="text-sm font-medium text-gray-900">Element Details</h5>
                            <button
                              onClick={() => startElementEdit(element.id)}
                              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                            >
                              <PencilIcon className="h-4 w-4 mr-2" />
                              Edit
                            </button>
                          </div>

                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Element Information */}
                            <div>
                              <h6 className="text-sm font-medium text-gray-900 mb-3">Element Information</h6>
                              <dl className="space-y-2">
                                <div className="flex justify-between">
                                  <dt className="text-sm text-gray-500">Type</dt>
                                  <dd className="text-sm text-gray-900">{element.element_type.replace('_', ' ')}</dd>
                                </div>
                                <div className="flex justify-between">
                                  <dt className="text-sm text-gray-500">Status</dt>
                                  <dd className="text-sm text-gray-900">{element.status}</dd>
                                </div>
                                <div className="flex justify-between">
                                  <dt className="text-sm text-gray-500">Executions</dt>
                                  <dd className="text-sm text-gray-900">{element.execution_count}</dd>
                                </div>
                                <div className="flex justify-between">
                                  <dt className="text-sm text-gray-500">Created</dt>
                                  <dd className="text-sm text-gray-900">{formatDate(element.created_at)}</dd>
                                </div>
                                <div className="flex justify-between">
                                  <dt className="text-sm text-gray-500">Updated</dt>
                                  <dd className="text-sm text-gray-900">{formatDate(element.updated_at)}</dd>
                                </div>
                              </dl>
                            </div>

                            {/* Template Preview */}
                            <div>
                              <h6 className="text-sm font-medium text-gray-900 mb-3">Template Preview</h6>
                              <div className="bg-white rounded-md border border-gray-200 p-4">
                                <pre className="text-xs text-gray-800 whitespace-pre-wrap font-mono overflow-x-auto">
                                  {elementDetails.get(element.id)?.template?.content || 
                                   elementDetails.get(element.id)?.template_content || 
                                   'Loading template content...'}
                                </pre>
                              </div>
                            </div>
                          </div>

                          {/* Variables */}
                          {(elementDetails.get(element.id)?.template?.variables || elementDetails.get(element.id)?.template_variables || []).length > 0 && (
                            <div>
                              <h6 className="text-sm font-medium text-gray-900 mb-3">Template Variables</h6>
                              <div className="flex flex-wrap gap-2">
                                {(elementDetails.get(element.id)?.template?.variables || elementDetails.get(element.id)?.template_variables || []).map((variable: string, index: number) => (
                                  <span
                                    key={index}
                                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                                  >
                                    {variable}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Tags */}
                          {element.tags.length > 0 && (
                            <div>
                              <h6 className="text-sm font-medium text-gray-900 mb-3">Tags</h6>
                              <div className="flex flex-wrap gap-2">
                                {element.tags.map((tag, index) => (
                                  <span
                                    key={index}
                                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                                  >
                                    <HashtagIcon className="h-3 w-3 mr-1" />
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Actions */}
                          <div className="flex space-x-3">
                            <button
                              onClick={() => router.push(`/elements/${element.id}`)}
                              className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                            >
                              <EyeIcon className="h-4 w-4 mr-2" />
                              View Details
                            </button>
                            <button
                              onClick={() => console.log('Execute element:', element.id)}
                              className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                            >
                              <PlayIcon className="h-4 w-4 mr-2" />
                              Execute
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalElementPages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setElementsPage(Math.max(1, elementsPage - 1))}
                  disabled={elementsPage <= 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setElementsPage(Math.min(totalElementPages, elementsPage + 1))}
                  disabled={elementsPage >= totalElementPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing{' '}
                    <span className="font-medium">
                      {(elementsPage - 1) * elementsPageSize + 1}
                    </span>{' '}
                    to{' '}
                    <span className="font-medium">
                      {Math.min(elementsPage * elementsPageSize, totalElements)}
                    </span>{' '}
                    of{' '}
                    <span className="font-medium">{totalElements}</span> results
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button
                      onClick={() => setElementsPage(Math.max(1, elementsPage - 1))}
                      disabled={elementsPage <= 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeftPageIcon className="h-5 w-5" />
                    </button>
                    {Array.from({ length: totalElementPages }, (_, i) => i + 1).map((page) => (
                      <button
                        key={page}
                        onClick={() => setElementsPage(page)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          page === elementsPage
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {page}
                      </button>
                    ))}
                    <button
                      onClick={() => setElementsPage(Math.min(totalElementPages, elementsPage + 1))}
                      disabled={elementsPage >= totalElementPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRightPageIcon className="h-5 w-5" />
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );

  const renderProjectGenerations = () => {
    const totalGenerationPages = Math.ceil(totalGenerations / generationsPageSize);

    const getStatusIcon = (status: string) => {
      switch (status) {
        case 'completed':
          return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
        case 'failed':
          return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
        case 'processing':
          return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
        default:
          return <ClockIcon className="h-5 w-5 text-gray-400" />;
      }
    };

    const getStatusColor = (status: string) => {
      switch (status) {
        case 'completed':
          return 'bg-green-100 text-green-800';
        case 'failed':
          return 'bg-red-100 text-red-800';
        case 'processing':
          return 'bg-blue-100 text-blue-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    return (
      <div className="bg-white shadow rounded-lg">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">
              Generations ({totalGenerations})
            </h2>
            <button
              onClick={() => fetchGenerations(generationsPage)}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        {/* Loading State */}
        {isLoadingGenerations ? (
          <div className="text-center py-8">
            <LoadingSpinner size="md" />
            <p className="mt-2 text-gray-600">Loading generations...</p>
          </div>
        ) : (
          <>
            {/* Generations List */}
            {allGenerations.length > 0 ? (
              <div className="divide-y divide-gray-200">
                {allGenerations.map((generation) => (
                  <div key={generation.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(generation.status)}
                        <div>
                          <h3 className="text-sm font-medium text-gray-900">
                            Generation {generation.id.slice(-8)}
                          </h3>
                          <p className="text-sm text-gray-500">
                            Element: {generation.element_id?.slice(-8) || 'Unknown'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(generation.status)}`}>
                          {generation.status}
                        </span>
                        <span className="text-sm text-gray-500">
                          {formatDate(generation.created_at)}
                        </span>
                        <button
                          onClick={() => router.push(`/generations/${generation.id}`)}
                          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                        >
                          <EyeIcon className="h-4 w-4 mr-2" />
                          View
                        </button>
                      </div>
                    </div>

                    {/* Token and Cost Info */}
                    <div className="mt-4 grid grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-900">
                          {generation.token_usage || 0}
                        </div>
                        <div className="text-xs text-gray-500">Tokens</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-900">
                          {generation.chunk_count || 0}
                        </div>
                        <div className="text-xs text-gray-500">Chunks</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-medium text-gray-900">
                          {generation.model_used || '—'}
                        </div>
                        <div className="text-xs text-gray-500">Model</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <SparklesIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No generations found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Generate content from elements to see results here.
                </p>
              </div>
            )}

            {/* Pagination */}
            {totalGenerationPages > 1 && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => fetchGenerations(Math.max(1, generationsPage - 1))}
                    disabled={generationsPage <= 1}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => fetchGenerations(Math.min(totalGenerationPages, generationsPage + 1))}
                    disabled={generationsPage >= totalGenerationPages}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing{' '}
                      <span className="font-medium">
                        {(generationsPage - 1) * generationsPageSize + 1}
                      </span>{' '}
                      to{' '}
                      <span className="font-medium">
                        {Math.min(generationsPage * generationsPageSize, totalGenerations)}
                      </span>{' '}
                      of{' '}
                      <span className="font-medium">{totalGenerations}</span> results
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                      <button
                        onClick={() => fetchGenerations(Math.max(1, generationsPage - 1))}
                        disabled={generationsPage <= 1}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <ChevronLeftPageIcon className="h-5 w-5" />
                      </button>
                      {Array.from({ length: totalGenerationPages }, (_, i) => i + 1).map((page) => (
                        <button
                          key={page}
                          onClick={() => fetchGenerations(page)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === generationsPage
                              ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      ))}
                      <button
                        onClick={() => fetchGenerations(Math.min(totalGenerationPages, generationsPage + 1))}
                        disabled={generationsPage >= totalGenerationPages}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <ChevronRightPageIcon className="h-5 w-5" />
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderProjectOverview();
      case 'documents':
        return renderProjectDocuments();
      case 'elements':
        return renderProjectElements();
      case 'generations':
        return renderProjectGenerations();
      case 'settings':
        return <div className="text-center py-8"><p className="text-gray-500">Settings view coming soon</p></div>;
      default:
        return renderProjectOverview();
    }
  };

  return (
    <DashboardLayout title={project.name}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/projects')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to Projects
          </button>
        </div>

        {/* Project Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    project.status === ProjectStatus.ACTIVE ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {project.status}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {getTenantTypeDisplay(project.tenant_type)}
                  </span>
                </div>
                <p className="text-gray-600">{project.description}</p>
              </div>
              <div className="flex items-center space-x-2">
                <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                  <UsersIcon className="h-4 w-4 mr-2" />
                  Collaborate
                </button>
                <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                  <Cog6ToothIcon className="h-4 w-4 mr-2" />
                  Settings
                </button>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-t border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </div>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {renderTabContent()}
      </div>
    </DashboardLayout>
  );
} 