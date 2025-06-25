'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  DocumentTextIcon,
  WrenchScrewdriverIcon,
  Cog6ToothIcon,
  PlusIcon,
  TrashIcon,
  EyeIcon,
  ChevronLeftIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ElementType, ElementStatus } from '@/types';

interface Variable {
  name: string;
  type: string;
  description: string;
  default_value?: string;
}

interface ElementFormData {
  name: string;
  description: string;
  type: ElementType;
  status: ElementStatus;
  template_content: string;
  variables: Variable[];
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
    variables: [],
    project_id: '1', // Mock project ID
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const elementTypes = [
    {
      type: ElementType.PROMPT_TEMPLATE,
      name: 'Prompt Template',
      description: 'Create templates for AI-powered text generation with variable substitution',
      icon: DocumentTextIcon,
      color: 'bg-blue-50 border-blue-200 text-blue-800',
      example: 'Based on the following context: {context}\n\nAnswer the user question: {question}\n\nProvide a helpful and accurate response.'
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
      description: 'Configure model connection protocols and AI provider settings',
      icon: Cog6ToothIcon,
      color: 'bg-purple-50 border-purple-200 text-purple-800',
      example: JSON.stringify({
        provider: 'openai',
        model: 'gpt-4-turbo',
        temperature: 0.7,
        max_tokens: 2000,
        system_prompt: 'You are a helpful assistant.'
      }, null, 2)
    }
  ];

  const handleTypeSelect = (type: ElementType) => {
    setSelectedType(type);
    setFormData(prev => ({
      ...prev,
      type,
      template_content: elementTypes.find(t => t.type === type)?.example || '',
      variables: type === ElementType.PROMPT_TEMPLATE ? [
        { name: 'context', type: 'string', description: 'Relevant context information' },
        { name: 'question', type: 'string', description: 'User question or query' }
      ] : []
    }));
  };

  const addVariable = () => {
    setFormData(prev => ({
      ...prev,
      variables: [...prev.variables, { name: '', type: 'string', description: '' }]
    }));
  };

  const updateVariable = (index: number, field: keyof Variable, value: string) => {
    setFormData(prev => ({
      ...prev,
      variables: prev.variables.map((variable, i) => 
        i === index ? { ...variable, [field]: value } : variable
      )
    }));
  };

  const removeVariable = (index: number) => {
    setFormData(prev => ({
      ...prev,
      variables: prev.variables.filter((_, i) => i !== index)
    }));
  };

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
      formData.variables.forEach(variable => {
        const placeholder = `{${variable.name}}`;
        const replacement = variable.default_value || `[${variable.name.toUpperCase()}]`;
        preview = preview.replace(new RegExp(placeholder, 'g'), replacement);
      });
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
           formData.template_content.trim() &&
           (formData.type !== ElementType.PROMPT_TEMPLATE || formData.variables.length > 0);
  };

  const selectedTypeInfo = elementTypes.find(t => t.type === selectedType);

  return (
    <DashboardLayout title="Create Element">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/elements')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <ChevronLeftIcon className="h-4 w-4 mr-1" />
            Back to Elements
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Type Selection */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Element Type</h3>
              <div className="grid grid-cols-1 gap-4">
                {elementTypes.map((type) => (
                  <div
                    key={type.type}
                    onClick={() => handleTypeSelect(type.type)}
                    className={`relative rounded-lg border-2 p-4 cursor-pointer transition-all ${
                      selectedType === type.type
                        ? type.color
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center">
                      <type.icon className="h-6 w-6 mr-3" />
                      <div className="flex-1">
                        <h4 className="text-sm font-medium">{type.name}</h4>
                        <p className="text-sm text-gray-500">{type.description}</p>
                      </div>
                      {selectedType === type.type && (
                        <div className="text-blue-600">
                          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Basic Information */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Element Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter a descriptive name for your element"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe what this element does and how it should be used"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as ElementStatus }))}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={ElementStatus.DRAFT}>Draft</option>
                    <option value={ElementStatus.ACTIVE}>Active</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Template Content */}
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {selectedType === ElementType.PROMPT_TEMPLATE ? 'Template Content' :
                   selectedType === ElementType.AGENTIC_TOOL ? 'Tool Configuration' :
                   'MCP Configuration'}
                </h3>
                <button
                  onClick={() => setShowPreview(!showPreview)}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <EyeIcon className="h-4 w-4 mr-1" />
                  {showPreview ? 'Hide Preview' : 'Show Preview'}
                </button>
              </div>

              <div className="space-y-4">
                <textarea
                  rows={12}
                  value={formData.template_content}
                  onChange={(e) => setFormData(prev => ({ ...prev, template_content: e.target.value }))}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder={selectedTypeInfo?.example}
                />

                {showPreview && (
                  <div className="border border-gray-200 rounded-md p-4 bg-gray-50">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Preview</h4>
                    <pre className="text-sm text-gray-600 whitespace-pre-wrap">
                      {generatePreview()}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {/* Variables (for prompt templates) */}
            {selectedType === ElementType.PROMPT_TEMPLATE && (
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Variables</h3>
                  <button
                    onClick={addVariable}
                    className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <PlusIcon className="h-4 w-4 mr-1" />
                    Add Variable
                  </button>
                </div>

                <div className="space-y-3">
                  {formData.variables.map((variable, index) => (
                    <div key={index} className="grid grid-cols-12 gap-3 items-start">
                      <div className="col-span-3">
                        <input
                          type="text"
                          value={variable.name}
                          onChange={(e) => updateVariable(index, 'name', e.target.value)}
                          className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Variable name"
                        />
                      </div>
                      <div className="col-span-2">
                        <select
                          value={variable.type}
                          onChange={(e) => updateVariable(index, 'type', e.target.value)}
                          className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="string">String</option>
                          <option value="number">Number</option>
                          <option value="boolean">Boolean</option>
                          <option value="array">Array</option>
                        </select>
                      </div>
                      <div className="col-span-5">
                        <input
                          type="text"
                          value={variable.description}
                          onChange={(e) => updateVariable(index, 'description', e.target.value)}
                          className="block w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="Description"
                        />
                      </div>
                      <div className="col-span-2">
                        <button
                          onClick={() => removeVariable(index)}
                          className="w-full inline-flex items-center justify-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {formData.variables.length === 0 && (
                  <div className="text-center py-6 text-gray-500">
                    <p className="text-sm">No variables defined yet. Click "Add Variable" to get started.</p>
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => router.push('/elements')}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={!isFormValid() || isSubmitting}
                className={`px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white ${
                  isFormValid() && !isSubmitting
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2 inline-block" />
                    Creating...
                  </>
                ) : (
                  'Create Element'
                )}
              </button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Help */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Help & Tips</h3>
              
              {selectedType === ElementType.PROMPT_TEMPLATE && (
                <div className="space-y-3">
                  <div className="flex">
                    <InformationCircleIcon className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium">Variable Syntax</p>
                      <p>Use {'{variable_name}'} to insert variables in your template.</p>
                    </div>
                  </div>
                  <div className="flex">
                    <InformationCircleIcon className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium">Best Practices</p>
                      <p>Be specific about the context and expected output format.</p>
                    </div>
                  </div>
                </div>
              )}

              {selectedType === ElementType.AGENTIC_TOOL && (
                <div className="space-y-3">
                  <div className="flex">
                    <InformationCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium">Tool Definition</p>
                      <p>Define clear parameters and descriptions for AI agents to use.</p>
                    </div>
                  </div>
                  <div className="flex">
                    <InformationCircleIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium">JSON Format</p>
                      <p>Use valid JSON with tool_name, description, and parameters.</p>
                    </div>
                  </div>
                </div>
              )}

              {selectedType === ElementType.MCP_CONFIG && (
                <div className="space-y-3">
                  <div className="flex">
                    <InformationCircleIcon className="h-5 w-5 text-purple-500 mr-2 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium">Provider Settings</p>
                      <p>Configure model parameters like temperature and max_tokens.</p>
                    </div>
                  </div>
                  <div className="flex">
                    <InformationCircleIcon className="h-5 w-5 text-purple-500 mr-2 mt-0.5" />
                    <div className="text-sm text-gray-600">
                      <p className="font-medium">System Prompts</p>
                      <p>Set system prompts to define AI behavior and constraints.</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Element Statistics */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Usage Statistics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Executions</span>
                  <span className="text-sm font-medium text-gray-900">0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Success Rate</span>
                  <span className="text-sm font-medium text-gray-900">—</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Avg. Execution Time</span>
                  <span className="text-sm font-medium text-gray-900">—</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-500">Total Cost</span>
                  <span className="text-sm font-medium text-gray-900">$0.00</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 