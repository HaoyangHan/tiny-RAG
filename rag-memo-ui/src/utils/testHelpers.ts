/**
 * Test utilities and helpers for TinyRAG v1.4.1 frontend testing
 * Provides mock data, API mocking, and testing utilities
 */

import { 
  User, 
  Project, 
  Document, 
  Element, 
  Generation, 
  Evaluation,
  TenantType,
  ProjectStatus,
  VisibilityType,
  ElementType,
  ElementStatus,
  DocumentStatus,
  GenerationStatus,
  EvaluationStatus
} from '@/types';

// ============================================================================
// Mock Data Generators
// ============================================================================

export const createMockUser = (overrides?: Partial<User>): User => ({
  id: '1',
  email: 'test@example.com',
  username: 'testuser',
  full_name: 'Test User',
  avatar_url: 'https://avatar.example.com/test.jpg',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
});

export const createMockProject = (overrides?: Partial<Project>): Project => ({
  id: '1',
  name: 'Test Project',
  description: 'A test project for development',
  tenant_type: TenantType.RAW_RAG,
  keywords: ['test', 'development'],
  visibility: VisibilityType.PRIVATE,
  status: ProjectStatus.ACTIVE,
  owner_id: '1',
  collaborators: [],
  document_count: 5,
  element_count: 3,
  generation_count: 10,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
});

export const createMockDocument = (overrides?: Partial<Document>): Document => ({
  id: '1',
  filename: 'test-document.pdf',
  content_type: 'application/pdf',
  file_size: 1024000,
  project_id: '1',
  status: DocumentStatus.COMPLETED,
  chunk_count: 5,
  metadata: { title: 'Test Document', pages: 10 },
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
});

export const createMockElement = (overrides?: Partial<Element>): Element => ({
  id: '1',
  name: 'Test Element',
  description: 'A test element for development',
  project_id: '1',
  element_type: ElementType.PROMPT_TEMPLATE,
  status: ElementStatus.ACTIVE,
  template_version: '1.0.0',
  tags: ['test', 'template'],
  execution_count: 5,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
});

export const createMockGeneration = (overrides?: Partial<Generation>): Generation => ({
  id: '1',
  element_id: '1',
  project_id: '1',
  status: GenerationStatus.COMPLETED,
  input_variables: { question: 'What is AI?', context: 'AI is artificial intelligence...' },
  output_content: 'AI is a technology that enables machines to simulate human intelligence.',
  model_used: 'gpt-4-turbo',
  token_usage: { prompt_tokens: 50, completion_tokens: 30, total_tokens: 80 },
  cost_usd: 0.01,
  execution_time_ms: 2000,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
});

export const createMockEvaluation = (overrides?: Partial<Evaluation>): Evaluation => ({
  id: '1',
  generation_id: '1',
  project_id: '1',
  status: EvaluationStatus.COMPLETED,
  overall_score: 4.5,
  criteria_scores: { accuracy: 5, relevance: 4, clarity: 4 },
  evaluator_model: 'gpt-4',
  hallucination_detected: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides
});

// ============================================================================
// Mock API Responses
// ============================================================================

export const createMockPaginatedResponse = <T>(
  items: T[], 
  page = 1, 
  pageSize = 20,
  totalCount?: number
) => ({
  items,
  total_count: totalCount || items.length,
  page,
  page_size: pageSize,
  has_next: (page * pageSize) < (totalCount || items.length),
  has_prev: page > 1
});

export const createMockAuthResponse = (user?: Partial<User>) => ({
  access_token: 'mock-jwt-token',
  token_type: 'Bearer',
  expires_in: 3600,
  user: createMockUser(user)
});

export const createMockAnalyticsResponse = () => ({
  total_projects: 5,
  total_documents: 25,
  total_elements: 15,
  total_generations: 100,
  total_cost: 25.50,
  recent_activity: [
    {
      type: 'generation_completed',
      description: 'Generated response for customer query',
      timestamp: '2024-01-01T12:00:00Z'
    },
    {
      type: 'document_uploaded',
      description: 'Uploaded new FAQ document',
      timestamp: '2024-01-01T11:30:00Z'
    }
  ]
});

// ============================================================================
// Test Environment Setup
// ============================================================================

export const setupTestEnvironment = () => {
  // Mock localStorage
  const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
  };
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock
  });

  // Mock fetch
  global.fetch = jest.fn();

  // Mock WebSocket
  global.WebSocket = jest.fn().mockImplementation(() => ({
    readyState: WebSocket.OPEN,
    send: jest.fn(),
    close: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  })) as any;

  // Mock URL.createObjectURL
  global.URL.createObjectURL = jest.fn(() => 'mocked-object-url');
  global.URL.revokeObjectURL = jest.fn();

  // Mock navigator.clipboard
  Object.defineProperty(navigator, 'clipboard', {
    value: {
      writeText: jest.fn(() => Promise.resolve()),
      readText: jest.fn(() => Promise.resolve(''))
    }
  });

  return {
    localStorage: localStorageMock,
    fetch: global.fetch,
    WebSocket: global.WebSocket
  };
};

// ============================================================================
// API Mocking Utilities
// ============================================================================

export const mockApiSuccess = <T>(data: T, delay = 100) => {
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(data),
    headers: new Headers(),
    redirected: false,
    statusText: 'OK',
    type: 'basic' as ResponseType,
    url: '',
    clone: jest.fn(),
    body: null,
    bodyUsed: false,
    arrayBuffer: jest.fn(),
    blob: jest.fn(),
    formData: jest.fn(),
    text: jest.fn(),
  } as Response);
};

export const mockApiError = (status = 500, message = 'Internal Server Error') => {
  return Promise.resolve({
    ok: false,
    status,
    json: () => Promise.resolve({ detail: message }),
    headers: new Headers(),
    redirected: false,
    statusText: message,
    type: 'basic' as ResponseType,
    url: '',
    clone: jest.fn(),
    body: null,
    bodyUsed: false,
    arrayBuffer: jest.fn(),
    blob: jest.fn(),
    formData: jest.fn(),
    text: jest.fn(),
  } as Response);
};

// ============================================================================
// File Testing Utilities
// ============================================================================

export const createMockFile = (
  name = 'test.pdf',
  size = 1024,
  type = 'application/pdf'
): File => {
  const blob = new Blob(['test content'], { type });
  return new File([blob], name, { type, lastModified: Date.now() });
};

export const createMockFileList = (files: File[]): FileList => {
  const fileList = {
    length: files.length,
    item: (index: number) => files[index] || null,
    [Symbol.iterator]: function* () {
      for (let i = 0; i < files.length; i++) {
        yield files[i];
      }
    }
  };

  // Add array-like access
  files.forEach((file, index) => {
    (fileList as any)[index] = file;
  });

  return fileList as FileList;
};

// ============================================================================
// WebSocket Testing Utilities
// ============================================================================

export const createMockWebSocketMessage = (type: string, data: any) => ({
  type,
  data,
  timestamp: new Date().toISOString(),
  project_id: '1',
  user_id: '1'
});

export const simulateWebSocketMessage = (
  message: any,
  eventType = 'websocket-message'
) => {
  window.dispatchEvent(new CustomEvent(eventType, { detail: message }));
};

// ============================================================================
// Form Testing Utilities
// ============================================================================

export const simulateFormSubmit = (form: HTMLFormElement, data: Record<string, string>) => {
  Object.keys(data).forEach(key => {
    const input = form.querySelector(`[name="${key}"]`) as HTMLInputElement;
    if (input) {
      input.value = data[key];
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }
  });

  form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
};

// ============================================================================
// Performance Testing Utilities
// ============================================================================

export const measurePerformance = async (fn: () => Promise<void> | void): Promise<number> => {
  const start = performance.now();
  await fn();
  const end = performance.now();
  return end - start;
};

export const simulateSlowNetwork = (delay = 2000) => {
  return new Promise(resolve => setTimeout(resolve, delay));
};

// ============================================================================
// Accessibility Testing Helpers
// ============================================================================

export const checkAccessibility = (element: HTMLElement): string[] => {
  const issues: string[] = [];

  // Check for missing alt text on images
  const images = element.querySelectorAll('img');
  images.forEach(img => {
    if (!img.alt) {
      issues.push('Image missing alt text');
    }
  });

  // Check for missing labels on form controls
  const formControls = element.querySelectorAll('input, select, textarea');
  formControls.forEach(control => {
    const hasLabel = control.labels && control.labels.length > 0;
    const hasAriaLabel = control.getAttribute('aria-label');
    const hasAriaLabelledBy = control.getAttribute('aria-labelledby');

    if (!hasLabel && !hasAriaLabel && !hasAriaLabelledBy) {
      issues.push('Form control missing accessible label');
    }
  });

  // Check for proper heading hierarchy
  const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6');
  let lastLevel = 0;
  headings.forEach(heading => {
    const level = parseInt(heading.tagName.substring(1));
    if (level > lastLevel + 1) {
      issues.push('Heading level skipped');
    }
    lastLevel = level;
  });

  return issues;
};

// ============================================================================
// Error Testing Utilities
// ============================================================================

export const simulateNetworkError = () => {
  return Promise.reject(new Error('Network request failed'));
};

export const simulateTimeoutError = () => {
  return Promise.reject(new Error('Request timeout'));
};

export const simulateAuthenticationError = () => {
  return Promise.reject({ status: 401, message: 'Authentication required' });
};

export default {
  createMockUser,
  createMockProject,
  createMockDocument,
  createMockElement,
  createMockGeneration,
  createMockEvaluation,
  createMockPaginatedResponse,
  createMockAuthResponse,
  createMockAnalyticsResponse,
  setupTestEnvironment,
  mockApiSuccess,
  mockApiError,
  createMockFile,
  createMockFileList,
  createMockWebSocketMessage,
  simulateWebSocketMessage,
  simulateFormSubmit,
  measurePerformance,
  simulateSlowNetwork,
  checkAccessibility,
  simulateNetworkError,
  simulateTimeoutError,
  simulateAuthenticationError
}; 