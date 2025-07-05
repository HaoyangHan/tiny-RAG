'use client';

import React, { useState } from 'react';
import APITestSuite from '@/components/testing/APITestSuite';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { api } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

export default function TestingPage() {
  const [testResults, setTestResults] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated, user } = useAuthStore();

  const testGenerationsAPI = async () => {
    setIsLoading(true);
    setTestResults('');
    
    try {
      const projectId = '68654518371d2079ca0c2fab';
      
      // Test the API call directly
      console.log('Testing generations API...');
      const response = await api.getGenerations({
        project_id: projectId,
        page_size: 5,
        include_content: true
      });
      
      const result = `
=== GENERATIONS API TEST RESULTS ===
✅ API Call Successful
Total Count: ${response.total_count}
Items Count: ${response.items.length}
First Item: ${JSON.stringify(response.items[0], null, 2)}

Auth Status: ${isAuthenticated ? 'Authenticated' : 'Not authenticated'}
User: ${user?.username || 'No user'}
Token: ${(api as any).token ? 'Token exists' : 'No token'}
======================================
      `;
      
      setTestResults(result);
      console.log('Generations API test results:', response);
      
    } catch (error) {
      const errorResult = `
=== GENERATIONS API TEST FAILED ===
❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}
Auth Status: ${isAuthenticated ? 'Authenticated' : 'Not authenticated'}
User: ${user?.username || 'No user'}
Token: ${(api as any).token ? 'Token exists' : 'No token'}
Full Error: ${JSON.stringify(error, null, 2)}
==================================
      `;
      
      setTestResults(errorResult);
      console.error('Generations API test failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-4">Generation API Debug Test</h1>
          <button
            onClick={testGenerationsAPI}
            disabled={isLoading}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
          >
            {isLoading ? 'Testing...' : 'Test Generations API'}
          </button>
        </div>
        
        {testResults && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Test Results:</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-x-auto text-sm">
              {testResults}
            </pre>
          </div>
        )}
        
        <APITestSuite />
      </div>
    </DashboardLayout>
  );
} 