'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FolderIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { TenantType, ProjectStatus, VisibilityType } from '@/types';

interface ProjectFormData {
  name: string;
  description: string;
  tenant_type: TenantType;
  visibility: VisibilityType;
  keywords: string[];
  collaborators: string[];
}

export default function CreateProjectPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<ProjectFormData>({
    name: '',
    description: '',
    tenant_type: TenantType.INDIVIDUAL,
    visibility: VisibilityType.PRIVATE,
    keywords: [],
    collaborators: [],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newKeyword, setNewKeyword] = useState('');
  const [newCollaborator, setNewCollaborator] = useState('');

  const steps = [
    { id: 1, name: 'Basic Details', description: 'Project name and description' },
    { id: 2, name: 'Configuration', description: 'Settings and permissions' },
    { id: 3, name: 'Confirmation', description: 'Review and create' },
  ];

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !formData.keywords.includes(newKeyword.trim())) {
      setFormData(prev => ({
        ...prev,
        keywords: [...prev.keywords, newKeyword.trim()]
      }));
      setNewKeyword('');
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keyword)
    }));
  };

  const handleAddCollaborator = () => {
    if (newCollaborator.trim() && !formData.collaborators.includes(newCollaborator.trim())) {
      setFormData(prev => ({
        ...prev,
        collaborators: [...prev.collaborators, newCollaborator.trim()]
      }));
      setNewCollaborator('');
    }
  };

  const handleRemoveCollaborator = (collaborator: string) => {
    setFormData(prev => ({
      ...prev,
      collaborators: prev.collaborators.filter(c => c !== collaborator)
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Mock API call - replace with actual implementation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Navigate to the new project
      router.push('/projects/1'); // Mock project ID
    } catch (error) {
      console.error('Failed to create project:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isStepValid = (step: number): boolean => {
    switch (step) {
      case 1:
        return formData.name.trim().length > 0 && formData.description.trim().length > 0;
      case 2:
        return true; // Configuration step is always valid (optional fields)
      case 3:
        return isStepValid(1) && isStepValid(2);
      default:
        return false;
    }
  };

  // Step indicator render function
  const renderStepIndicator = () => (
    <div className="mb-8">
      <nav aria-label="Progress">
        <ol className="flex items-center">
          {steps.map((step, stepIdx) => (
            <li key={step.id} className={`${stepIdx !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''} relative`}>
              <div className="flex items-center">
                <div
                  className={`relative flex h-8 w-8 items-center justify-center rounded-full ${
                    step.id < currentStep
                      ? 'bg-blue-600'
                      : step.id === currentStep
                      ? 'border-2 border-blue-600 bg-white'
                      : 'border-2 border-gray-300 bg-white'
                  }`}
                >
                  {step.id < currentStep ? (
                    <CheckIcon className="h-5 w-5 text-white" />
                  ) : (
                    <span
                      className={`text-sm font-medium ${
                        step.id === currentStep ? 'text-blue-600' : 'text-gray-500'
                      }`}
                    >
                      {step.id}
                    </span>
                  )}
                </div>
                <div className="ml-4 min-w-0 flex flex-col">
                  <span
                    className={`text-sm font-medium ${
                      step.id <= currentStep ? 'text-blue-600' : 'text-gray-500'
                    }`}
                  >
                    {step.name}
                  </span>
                  <span className="text-sm text-gray-500">{step.description}</span>
                </div>
              </div>
              {stepIdx !== steps.length - 1 && (
                <div className="absolute top-4 left-8 -ml-px mt-0.5 h-px w-8 sm:w-20 bg-gray-300" />
              )}
            </li>
          ))}
        </ol>
      </nav>
    </div>
  );

  // Basic details step render function
  const renderBasicDetailsStep = () => (
    <div className="space-y-6">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
          Project Name *
        </label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Enter a descriptive name for your project"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Description *
        </label>
        <textarea
          id="description"
          rows={4}
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Describe what this RAG project will accomplish"
        />
      </div>

      <div>
        <label htmlFor="tenant_type" className="block text-sm font-medium text-gray-700 mb-2">
          Tenant Type
        </label>
        <select
          id="tenant_type"
          value={formData.tenant_type}
          onChange={(e) => setFormData(prev => ({ ...prev, tenant_type: e.target.value as TenantType }))}
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value={TenantType.INDIVIDUAL}>Individual</option>
          <option value={TenantType.TEAM}>Team</option>
          <option value={TenantType.ORGANIZATION}>Organization</option>
          <option value={TenantType.ENTERPRISE}>Enterprise</option>
        </select>
        <p className="mt-1 text-sm text-gray-500">
          This determines the collaboration features and resource limits for your project.
        </p>
      </div>
    </div>
  );

  // Configuration step render function
  const renderConfigurationStep = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Visibility
        </label>
        <div className="space-y-3">
          <label className="flex items-center">
            <input
              type="radio"
              name="visibility"
              value={VisibilityType.PRIVATE}
              checked={formData.visibility === VisibilityType.PRIVATE}
              onChange={(e) => setFormData(prev => ({ ...prev, visibility: e.target.value as VisibilityType }))}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-3 text-sm text-gray-700">
              <strong>Private</strong> - Only you and invited collaborators can access
            </span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              name="visibility"
              value={VisibilityType.PUBLIC}
              checked={formData.visibility === VisibilityType.PUBLIC}
              onChange={(e) => setFormData(prev => ({ ...prev, visibility: e.target.value as VisibilityType }))}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
            />
            <span className="ml-3 text-sm text-gray-700">
              <strong>Public</strong> - Anyone in your organization can view
            </span>
          </label>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Keywords
        </label>
        <div className="flex items-center space-x-2 mb-3">
          <input
            type="text"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddKeyword()}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add keywords to help organize your project"
          />
          <button
            type="button"
            onClick={handleAddKeyword}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.keywords.map((keyword) => (
            <span
              key={keyword}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
            >
              {keyword}
              <button
                type="button"
                onClick={() => handleRemoveKeyword(keyword)}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Collaborators
        </label>
        <div className="flex items-center space-x-2 mb-3">
          <input
            type="email"
            value={newCollaborator}
            onChange={(e) => setNewCollaborator(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddCollaborator()}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter email address to invite collaborators"
          />
          <button
            type="button"
            onClick={handleAddCollaborator}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Invite
          </button>
        </div>
        <div className="space-y-2">
          {formData.collaborators.map((collaborator) => (
            <div
              key={collaborator}
              className="flex items-center justify-between p-2 bg-gray-50 rounded-md"
            >
              <span className="text-sm text-gray-700">{collaborator}</span>
              <button
                type="button"
                onClick={() => handleRemoveCollaborator(collaborator)}
                className="text-red-600 hover:text-red-800"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Confirmation step render function
  const renderConfirmationStep = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <FolderIcon className="h-8 w-8 text-blue-600 mr-3" />
          <h3 className="text-lg font-medium text-blue-900">Review Your Project</h3>
        </div>
        
        <dl className="space-y-4">
          <div>
            <dt className="text-sm font-medium text-gray-700">Name</dt>
            <dd className="text-sm text-gray-900">{formData.name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-700">Description</dt>
            <dd className="text-sm text-gray-900">{formData.description}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-700">Type</dt>
            <dd className="text-sm text-gray-900">{formData.tenant_type}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-700">Visibility</dt>
            <dd className="text-sm text-gray-900">{formData.visibility}</dd>
          </div>
          {formData.keywords.length > 0 && (
            <div>
              <dt className="text-sm font-medium text-gray-700">Keywords</dt>
              <dd className="text-sm text-gray-900">{formData.keywords.join(', ')}</dd>
            </div>
          )}
          {formData.collaborators.length > 0 && (
            <div>
              <dt className="text-sm font-medium text-gray-700">Collaborators</dt>
              <dd className="text-sm text-gray-900">{formData.collaborators.join(', ')}</dd>
            </div>
          )}
        </dl>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <InformationCircleIcon className="h-5 w-5 text-yellow-400 mr-2 mt-0.5" />
          <div className="text-sm text-yellow-800">
            <p className="font-medium">Next Steps</p>
            <p className="mt-1">
              After creating your project, you'll be able to upload documents, create elements, and start generating content.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <DashboardLayout title="Create Project">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          <div className="p-8">
            {renderStepIndicator()}

            <div className="mb-8">
              {currentStep === 1 && renderBasicDetailsStep()}
              {currentStep === 2 && renderConfigurationStep()}
              {currentStep === 3 && renderConfirmationStep()}
            </div>

            {/* Navigation Buttons */}
            <div className="flex justify-between">
              <button
                type="button"
                onClick={handleBack}
                disabled={currentStep === 1}
                className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium ${
                  currentStep === 1
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-gray-700 bg-white hover:bg-gray-50'
                }`}
              >
                <ChevronLeftIcon className="h-5 w-5 mr-2" />
                Back
              </button>

              {currentStep < 3 ? (
                <button
                  type="button"
                  onClick={handleNext}
                  disabled={!isStepValid(currentStep)}
                  className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    isStepValid(currentStep)
                      ? 'bg-blue-600 hover:bg-blue-700'
                      : 'bg-gray-400 cursor-not-allowed'
                  }`}
                >
                  Next
                  <ChevronRightIcon className="h-5 w-5 ml-2" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={!isStepValid(3) || isSubmitting}
                  className={`inline-flex items-center px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                    isStepValid(3) && !isSubmitting
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-gray-400 cursor-not-allowed'
                  }`}
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                      Creating...
                    </>
                  ) : (
                    'Create Project'
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 