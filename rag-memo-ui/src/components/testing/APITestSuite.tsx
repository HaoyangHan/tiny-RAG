'use client';

import React, { useState, useEffect } from 'react';
import { api, APIError } from '@/services/api';
import { useAuth } from '@/stores/authStore';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ClockIcon,
  PlayIcon,
  StopIcon
} from '@heroicons/react/24/outline';

interface TestResult {
  name: string;
  status: 'pending' | 'running' | 'success' | 'error';
  duration?: number;
  error?: string;
  response?: any;
}

interface TestSuite {
  name: string;
  tests: TestResult[];
  status: 'pending' | 'running' | 'success' | 'error';
}

export const APITestSuite: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedSuite, setSelectedSuite] = useState<string | null>(null);

  const updateTestResult = (
    suiteName: string, 
    testName: string, 
    update: Partial<TestResult>
  ) => {
    setTestSuites(prev => prev.map(suite => {
      if (suite.name !== suiteName) return suite;
      
      const updatedTests = suite.tests.map(test => 
        test.name === testName ? { ...test, ...update } : test
      );
      
      const allCompleted = updatedTests.every(t => t.status === 'success' || t.status === 'error');
      const hasErrors = updatedTests.some(t => t.status === 'error');
      
      return {
        ...suite,
        tests: updatedTests,
        status: allCompleted ? (hasErrors ? 'error' : 'success') : 'running'
      };
    }));
  };

  const runTest = async (
    suiteName: string,
    testName: string,
    testFn: () => Promise<any>
  ): Promise<void> => {
    updateTestResult(suiteName, testName, { status: 'running' });
    
    const startTime = performance.now();
    
    try {
      const response = await testFn();
      const duration = performance.now() - startTime;
      
      updateTestResult(suiteName, testName, {
        status: 'success',
        duration: Math.round(duration),
        response
      });
    } catch (error) {
      const duration = performance.now() - startTime;
      const errorMessage = error instanceof APIError 
        ? `${error.status}: ${error.message}`
        : error instanceof Error 
        ? error.message 
        : 'Unknown error';
      
      updateTestResult(suiteName, testName, {
        status: 'error',
        duration: Math.round(duration),
        error: errorMessage
      });
    }
  };

  const initializeTestSuites = () => {
    const suites: TestSuite[] = [
      {
        name: 'Health & Status',
        status: 'pending',
        tests: [
          { name: 'Health Check', status: 'pending' },
          { name: 'API Connectivity', status: 'pending' }
        ]
      },
      {
        name: 'Authentication',
        status: 'pending',
        tests: [
          { name: 'Get Current User', status: 'pending' },
          { name: 'Token Validation', status: 'pending' }
        ]
      },
      {
        name: 'Projects',
        status: 'pending',
        tests: [
          { name: 'List Projects', status: 'pending' },
          { name: 'Create Project', status: 'pending' },
          { name: 'Get Project Details', status: 'pending' },
          { name: 'Update Project', status: 'pending' }
        ]
      },
      {
        name: 'Documents',
        status: 'pending',
        tests: [
          { name: 'List Documents', status: 'pending' },
          { name: 'Upload Document', status: 'pending' }
        ]
      },
      {
        name: 'Elements',
        status: 'pending',
        tests: [
          { name: 'List Elements', status: 'pending' },
          { name: 'Create Element', status: 'pending' },
          { name: 'Validate Template', status: 'pending' }
        ]
      },
      {
        name: 'Generations',
        status: 'pending',
        tests: [
          { name: 'List Generations', status: 'pending' },
          { name: 'Execute Element', status: 'pending' }
        ]
      },
      {
        name: 'Analytics',
        status: 'pending',
        tests: [
          { name: 'User Analytics', status: 'pending' }
        ]
      }
    ];

    setTestSuites(suites);
  };

  const runTestSuite = async (suiteName: string) => {
    const suite = testSuites.find(s => s.name === suiteName);
    if (!suite) return;

    // Mark suite as running
    setTestSuites(prev => prev.map(s => 
      s.name === suiteName ? { ...s, status: 'running' } : s
    ));

    switch (suiteName) {
      case 'Health & Status':
        await runTest(suiteName, 'Health Check', () => api.checkHealth());
        await runTest(suiteName, 'API Connectivity', () => 
          fetch(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
        );
        break;

      case 'Authentication':
        if (isAuthenticated) {
          await runTest(suiteName, 'Get Current User', () => api.getCurrentUser());
          await runTest(suiteName, 'Token Validation', async () => {
            const user = await api.getCurrentUser();
            if (!user?.id) throw new Error('Invalid user response');
            return user;
          });
        }
        break;

      case 'Projects':
        await runTest(suiteName, 'List Projects', () => api.getProjects({ page: 1, page_size: 5 }));
        
        let testProjectId: string | null = null;
        await runTest(suiteName, 'Create Project', async () => {
          const project = await api.createProject({
            name: `Test Project ${Date.now()}`,
            description: 'API test project',
            tenant_type: 'individual' as any,
            keywords: ['test', 'api'],
            visibility: 'private' as any
          });
          testProjectId = project.id;
          return project;
        });

        if (testProjectId) {
          await runTest(suiteName, 'Get Project Details', () => api.getProject(testProjectId!));
          await runTest(suiteName, 'Update Project', () => 
            api.updateProject(testProjectId!, { description: 'Updated test project' })
          );
        }
        break;

      case 'Documents':
        await runTest(suiteName, 'List Documents', () => api.getDocuments({ page: 1, page_size: 5 }));
        
        await runTest(suiteName, 'Upload Document', async () => {
          const testContent = 'This is a test document for API testing.';
          const blob = new Blob([testContent], { type: 'text/plain' });
          const file = new File([blob], 'test-document.txt', { type: 'text/plain' });
          return api.uploadDocument(file);
        });
        break;

      case 'Elements':
        await runTest(suiteName, 'List Elements', () => api.getElements({ page: 1, page_size: 5 }));
        
        await runTest(suiteName, 'Validate Template', () => 
          api.validateTemplate({
            template_content: 'Hello {{name}}, how can I help you with {{topic}}?',
            variables: ['name', 'topic'],
            element_type: 'prompt_template'
          })
        );

        await runTest(suiteName, 'Create Element', async () => {
          const projects = await api.getProjects({ page: 1, page_size: 1 });
          if (projects.items.length === 0) {
            throw new Error('No projects available for element creation');
          }
          
          return api.createElement({
            name: `Test Element ${Date.now()}`,
            description: 'API test element',
            project_id: projects.items[0].id,
            element_type: 'prompt_template' as any,
            template_content: 'Test template: {{input}}',
            variables: ['input']
          });
        });
        break;

      case 'Generations':
        await runTest(suiteName, 'List Generations', () => api.getGenerations({ page: 1, page_size: 5 }));
        
        await runTest(suiteName, 'Execute Element', async () => {
          const elements = await api.getElements({ page: 1, page_size: 1 });
          if (elements.items.length === 0) {
            throw new Error('No elements available for execution');
          }
          
          return api.executeElement(elements.items[0].id, { input: 'test input' });
        });
        break;

      case 'Analytics':
        await runTest(suiteName, 'User Analytics', () => api.getUserAnalytics());
        break;
    }
  };

  const runAllTests = async () => {
    setIsRunning(true);
    
    for (const suite of testSuites) {
      await runTestSuite(suite.name);
    }
    
    setIsRunning(false);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'running':
        return <ClockIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-50';
      case 'error': return 'text-red-600 bg-red-50';
      case 'running': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  useEffect(() => {
    initializeTestSuites();
  }, []);

  if (!isAuthenticated) {
    return (
      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">
          Please log in to run API tests. The test suite requires authentication to access most endpoints.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">TinyRAG API Test Suite</h1>
            <p className="text-gray-600 mt-1">
              Comprehensive testing of all API endpoints for production readiness
            </p>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={runAllTests}
              disabled={isRunning}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRunning ? (
                <>
                  <StopIcon className="h-4 w-4 mr-2" />
                  Running Tests...
                </>
              ) : (
                <>
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Run All Tests
                </>
              )}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {testSuites.map((suite) => (
            <div key={suite.name} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{suite.name}</h3>
                <button
                  onClick={() => runTestSuite(suite.name)}
                  disabled={isRunning}
                  className="text-sm px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                >
                  Run Suite
                </button>
              </div>
              
              <div className="space-y-2">
                {suite.tests.map((test) => (
                  <div
                    key={test.name}
                    className={`flex items-center justify-between p-3 rounded-md ${getStatusColor(test.status)}`}
                  >
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(test.status)}
                      <span className="text-sm font-medium">{test.name}</span>
                    </div>
                    
                    <div className="text-right">
                      {test.duration && (
                        <span className="text-xs text-gray-500">{test.duration}ms</span>
                      )}
                      {test.error && (
                        <div className="text-xs text-red-600 mt-1 max-w-xs truncate">
                          {test.error}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Test Summary</h4>
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">
                {testSuites.reduce((acc, suite) => 
                  acc + suite.tests.filter(t => t.status === 'success').length, 0
                )}
              </div>
              <div className="text-sm text-gray-500">Passed</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {testSuites.reduce((acc, suite) => 
                  acc + suite.tests.filter(t => t.status === 'error').length, 0
                )}
              </div>
              <div className="text-sm text-gray-500">Failed</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {testSuites.reduce((acc, suite) => 
                  acc + suite.tests.filter(t => t.status === 'running').length, 0
                )}
              </div>
              <div className="text-sm text-gray-500">Running</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-600">
                {testSuites.reduce((acc, suite) => acc + suite.tests.length, 0)}
              </div>
              <div className="text-sm text-gray-500">Total</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APITestSuite; 