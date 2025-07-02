'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  ChevronLeftIcon,
  DocumentTextIcon,
  CpuChipIcon,
  WrenchScrewdriverIcon,
  Cog6ToothIcon,
  CheckIcon,
  EyeIcon,
  PlusIcon,
  TrashIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ElementType, ElementStatus } from '@/types';

// Variable interface removed - using simplified additional instructions approach

interface ElementFormData {
  name: string;
  description: string;
  type: ElementType;
  status: ElementStatus;
  template_content: string;
  additional_instructions_template: string;
  project_id: string;
}

export default function CreateElementPage() {
  const router = useRouter();
  const [selectedType, setSelectedType] = useState<ElementType>(ElementType.PROMPT_TEMPLATE);
  const [formData, setFormData] = useState<ElementFormData>({
    name: '',
    description: '',
    type: ElementType.PROMPT_TEMPLATE,
    status: ElementStatus.DRAFT,
    template_content: '',
    additional_instructions_template: '',
    project_id: '1', // Mock project ID
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  // Variable state removed - using simplified additional instructions approach

  const elementTypes = [
    {
      type: ElementType.PROMPT_TEMPLATE,
      name: 'Prompt Template',
      description: 'Create templates for AI-powered text generation with retrieval context and optional additional instructions',
      icon: DocumentTextIcon,
      color: 'bg-blue-50 border-blue-200 text-blue-800',
      example: 'You are an expert analyst. Based on the retrieved document chunks below, provide a comprehensive analysis.\n\n**Retrieved Document Chunks:**\n{retrieved_chunks}\n\n{additional_instructions}\n\n**Generated Analysis:**'
    },
    {
      type: ElementType.AGENTIC_TOOL,
      name: 'Agentic Tool',
      description: 'Define tools that AI agents can use to interact with external systems',
      icon: WrenchScrewdriverIcon,
      color: 'bg-green-50 border-green-200 text-green-800',
      example: JSON.stringify({
        tool_name: 'search_documents',
        description: 'Search through document database',
        parameters: {
          query: { type: 'string', description: 'Search query' },
          limit: { type: 'integer', description: 'Max results', default: 10 }
        }
      }, null, 2)
    },
    {
      type: ElementType.MCP_CONFIG,
      name: 'MCP Configuration',
      description: 'Model Context Protocol configurations for structured AI interactions',
      icon: Cog6ToothIcon,
      color: 'bg-purple-50 border-purple-200 text-purple-800',
      example: JSON.stringify({
        protocol_version: '1.0',
        server_info: {
          name: 'document-analyzer',
          version: '1.0.0'
        },
        capabilities: {
          resources: true,
          tools: true,
          prompts: true
        }
      }, null, 2)
    },
    {
      type: ElementType.RAG_CONFIG,
      name: 'RAG Configuration',
      description: 'Retrieval-Augmented Generation pipeline configurations',
      icon: CpuChipIcon,
      color: 'bg-orange-50 border-orange-200 text-orange-800',
      example: JSON.stringify({
        retrieval_config: {
          top_k: 5,
          similarity_threshold: 0.7,
          rerank: true
        },
        generation_config: {
          model: 'gpt-4-turbo',
          temperature: 0.3,
          max_tokens: 2000
        }
      }, null, 2)
    }
  ];

  const handleTypeSelect = (type: ElementType) => {
    setSelectedType(type);
    const selectedTypeInfo = elementTypes.find(t => t.type === type);
    setFormData(prev => ({
      ...prev,
      type,
      template_content: selectedTypeInfo?.example || ''
    }));
  };

  // Variable functions removed - using simplified additional instructions approach

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Mock API call - replace with actual implementation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Navigate to elements list
      router.push('/elements');
    } catch (error) {
      console.error('Failed to create element:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const generatePreview = () => {
    if (formData.type === ElementType.PROMPT_TEMPLATE) {
      let preview = formData.template_content;
      // Replace placeholders with example content
      preview = preview.replace(/\{retrieved_chunks\}/g, '[Retrieved document chunks would appear here]');
      preview = preview.replace(/\{additional_instructions\}/g, 
        formData.additional_instructions_template || '[Optional additional instructions from user]');
      return preview;
    } else {
      try {
        return JSON.stringify(JSON.parse(formData.template_content), null, 2);
      } catch {
        return formData.template_content;
      }
    }
  };

  const isFormValid = () => {
    return formData.name.trim() && 
           formData.description.trim() && 
           formData.template_content.trim();
  };

  const selectedTypeInfo = elementTypes.find(t => t.type === selectedType);

  // Element type selection render function
  const renderElementTypeSelection = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Choose Element Type</h3>
        <div className="grid grid-cols-1 gap-4">
          {elementTypes.map((type) => {
            const IconComponent = type.icon;
            return (
              <div
                key={type.type}
                className={`relative rounded-lg border-2 p-4 cursor-pointer transition-all ${
                  selectedType === type.type
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => {
                  setSelectedType(type.type);
                  setFormData(prev => ({
                    ...prev,
                    type: type.type,
                    template_content: type.example
                  }));
                }}
              >
                <div className="flex items-start space-x-4">
                  <div className={`p-2 rounded-lg ${type.color}`}>
                    <IconComponent className="h-6 w-6" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-medium text-gray-900">{type.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                  </div>
                  {selectedType === type.type && (
                    <CheckIcon className="h-5 w-5 text-blue-500" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  // Element configuration render function
  const renderElementConfiguration = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          {/* Basic Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Element Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  placeholder="Enter a descriptive name for your element"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Description *
                </label>
                <textarea
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                  placeholder="Describe what this element does and how it should be used"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as ElementStatus }))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                >
                  <option value={ElementStatus.DRAFT}>Draft</option>
                  <option value={ElementStatus.ACTIVE}>Active</option>
                  <option value={ElementStatus.ARCHIVED}>Archived</option>
                </select>
              </div>
            </div>
          </div>

          {/* Template Content */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Template Content</h3>
              <button
                type="button"
                onClick={() => setShowPreview(!showPreview)}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                {showPreview ? 'Hide Preview' : 'Show Preview'}
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Template *
                </label>
                <textarea
                  rows={12}
                  value={formData.template_content}
                  onChange={(e) => setFormData(prev => ({ ...prev, template_content: e.target.value }))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-gray-900"
                  placeholder="Enter your template content here..."
                />
                <p className="mt-1 text-sm text-gray-700">
                  {selectedType === ElementType.PROMPT_TEMPLATE 
                    ? 'Use {retrieved_chunks} and {additional_instructions} placeholders for dynamic content'
                    : 'Use JSON syntax for configuration templates'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* Additional Instructions Template */}
          {selectedType === ElementType.PROMPT_TEMPLATE && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <h3 className="text-lg font-medium text-gray-900">Additional Instructions Template</h3>
                <InformationCircleIcon className="h-5 w-5 text-gray-400" />
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Instructions Template (Optional)
                  </label>
                  <textarea
                    rows={4}
                    value={formData.additional_instructions_template}
                    onChange={(e) => setFormData(prev => ({ ...prev, additional_instructions_template: e.target.value }))}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                    placeholder="e.g., Additional focus areas: [emphasize financial risks, focus on growth trends, etc.]"
                  />
                  <p className="mt-1 text-sm text-gray-600">
                    This template helps users understand what kind of additional instructions they can provide when using this element.
                  </p>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start space-x-2">
                    <InformationCircleIcon className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium text-blue-900">Simplified Generation Flow</h4>
                      <p className="text-sm text-blue-800 mt-1">
                        Elements now work with retrieved document chunks plus optional additional instructions. 
                        No complex variables needed - just clean, consistent generation.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Preview */}
          {showPreview && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Preview</h3>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                  {generatePreview()}
                </pre>
              </div>
            </div>
          )}

          {/* Element Type Info */}
          {selectedTypeInfo && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className={`p-2 rounded-lg ${selectedTypeInfo.color}`}>
                  <selectedTypeInfo.icon className="h-5 w-5" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">{selectedTypeInfo.name}</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">{selectedTypeInfo.description}</p>
              
              <div className="space-y-3">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Key Features:</h4>
                  <ul className="mt-1 text-sm text-gray-600 space-y-1">
                    {selectedType === ElementType.PROMPT_TEMPLATE && (
                      <>
                        <li>• Works with retrieved document chunks</li>
                        <li>• Supports optional additional instructions</li>
                        <li>• Optimized for RAG workflows</li>
                        <li>• Simple and consistent generation</li>
                      </>
                    )}
                    {selectedType === ElementType.AGENTIC_TOOL && (
                      <>
                        <li>• Function definitions for AI agents</li>
                        <li>• Parameter specifications</li>
                        <li>• External system integrations</li>
                      </>
                    )}
                    {selectedType === ElementType.MCP_CONFIG && (
                      <>
                        <li>• Model Context Protocol setup</li>
                        <li>• Structured AI interactions</li>
                        <li>• Protocol compliance</li>
                      </>
                    )}
                                         {selectedType === ElementType.RAG_CONFIG && (
                       <>
                         <li>• Retrieval configuration</li>
                         <li>• Generation parameters</li>
                         <li>• Pipeline optimization</li>
                       </>
                     )}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/elements')}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
            >
              <ChevronLeftIcon className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Create New Element</h1>
              <p className="text-sm text-gray-600">
                Design reusable AI elements for your projects
              </p>
            </div>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  1
                </div>
                <span className="text-sm font-medium text-blue-600">Choose Type</span>
              </div>
              <div className="w-16 h-0.5 bg-gray-200"></div>
              <div className="flex items-center space-x-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  selectedType ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                }`}>
                  2
                </div>
                <span className={`text-sm font-medium ${
                  selectedType ? 'text-blue-600' : 'text-gray-400'
                }`}>Configure</span>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        {!selectedType ? renderElementTypeSelection() : renderElementConfiguration()}

        {/* Footer */}
        {selectedType && (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between">
              <button
                onClick={() => setSelectedType(ElementType.PROMPT_TEMPLATE)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Back to Type Selection
              </button>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => router.push('/elements')}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!isFormValid() || isSubmitting}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {isSubmitting && <LoadingSpinner size="sm" />}
                  <span>{isSubmitting ? 'Creating...' : 'Create Element'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
} 