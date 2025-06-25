/**
 * TinyRAG v1.4.1 API Service Layer
 * 
 * Centralized API client with authentication, error handling,
 * and typed responses for all backend endpoints.
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  User,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  Project,
  ProjectCreateRequest,
  Element,
  ElementCreateRequest,
  Generation,
  Document,
  BulkExecutionStatus,
  TemplateValidationRequest,
  TemplateValidationResponse,
  PaginatedResponse,
  APIError
} from '@/types';

// ============================================================================
// API Client Configuration
// ============================================================================

class APIClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        const apiError: APIError = {
          status: error.response?.status || 500,
          message: error.response?.data?.detail || error.message || 'Unknown error',
          details: error.response?.data
        };
        return Promise.reject(apiError);
      }
    );
  }

  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
  }

  public setAuthToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  public clearAuthToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // ============================================================================
  // Authentication API
  // ============================================================================

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.client.post('/api/v1/auth/login', credentials);
    const authResponse = response.data;
    this.setAuthToken(authResponse.access_token);
    return authResponse;
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await this.client.post('/api/v1/auth/register', userData);
    const authResponse = response.data;
    this.setAuthToken(authResponse.access_token);
    return authResponse;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.client.post('/api/v1/auth/logout');
    } finally {
      this.clearAuthToken();
    }
  }

  // ============================================================================
  // Projects API
  // ============================================================================

  async getProjects(params?: {
    page?: number;
    page_size?: number;
    tenant_type?: string;
    status?: string;
    search?: string;
  }): Promise<PaginatedResponse<Project>> {
    const response = await this.client.get('/api/v1/projects', { params });
    return response.data;
  }

  async getProject(id: string): Promise<Project> {
    const response = await this.client.get(`/api/v1/projects/${id}`);
    return response.data;
  }

  async createProject(data: ProjectCreateRequest): Promise<Project> {
    const response = await this.client.post('/api/v1/projects', data);
    return response.data;
  }

  async updateProject(id: string, data: Partial<ProjectCreateRequest>): Promise<Project> {
    const response = await this.client.put(`/api/v1/projects/${id}`, data);
    return response.data;
  }

  async deleteProject(id: string): Promise<void> {
    await this.client.delete(`/api/v1/projects/${id}`);
  }

  // ============================================================================
  // Bulk Element Execution API (NEW)
  // ============================================================================

  async executeAllElements(
    projectId: string,
    elementIds?: string[]
  ): Promise<{ execution_id: string; message: string; status: string }> {
    const response = await this.client.post(
      `/api/v1/projects/${projectId}/elements/execute-all`,
      { element_ids: elementIds }
    );
    return response.data;
  }

  async getBulkExecutionStatus(
    projectId: string,
    executionId: string
  ): Promise<BulkExecutionStatus> {
    const response = await this.client.get(
      `/api/v1/projects/${projectId}/elements/execute-all-status`,
      { params: { execution_id: executionId } }
    );
    return response.data;
  }

  // ============================================================================
  // Elements API
  // ============================================================================

  async getElements(params?: {
    project_id?: string;
    element_type?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<Element[]> {
    const response = await this.client.get('/api/v1/elements', { params });
    return response.data;
  }

  async getElement(id: string): Promise<Element> {
    const response = await this.client.get(`/api/v1/elements/${id}`);
    return response.data;
  }

  async createElement(data: ElementCreateRequest): Promise<Element> {
    const response = await this.client.post('/api/v1/elements', data);
    return response.data;
  }

  async updateElement(id: string, data: Partial<ElementCreateRequest>): Promise<Element> {
    const response = await this.client.put(`/api/v1/elements/${id}`, data);
    return response.data;
  }

  async deleteElement(id: string): Promise<void> {
    await this.client.delete(`/api/v1/elements/${id}`);
  }

  async executeElement(
    id: string,
    variables: Record<string, any>
  ): Promise<Generation> {
    const response = await this.client.post(`/api/v1/elements/${id}/execute`, variables);
    return response.data;
  }

  // ============================================================================
  // Template Validation API (NEW)
  // ============================================================================

  async validateTemplate(data: TemplateValidationRequest): Promise<TemplateValidationResponse> {
    const response = await this.client.post('/api/v1/elements/validate-template', data);
    return response.data;
  }

  // ============================================================================
  // Generations API
  // ============================================================================

  async getGenerations(params?: {
    project_id?: string;
    element_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Generation>> {
    const response = await this.client.get('/api/v1/generations', { params });
    return response.data;
  }

  async getGeneration(id: string): Promise<Generation> {
    const response = await this.client.get(`/api/v1/generations/${id}`);
    return response.data;
  }

  // ============================================================================
  // Documents API
  // ============================================================================

  async getDocuments(params?: {
    project_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Document>> {
    const response = await this.client.get('/api/v1/documents', { params });
    return response.data;
  }

  async uploadDocument(
    projectId: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post(
      `/api/v1/documents/upload?project_id=${projectId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(progress);
          }
        },
      }
    );
    return response.data;
  }

  async deleteDocument(id: string): Promise<void> {
    await this.client.delete(`/api/v1/documents/${id}`);
  }

  // ============================================================================
  // Analytics API
  // ============================================================================

  async getUserAnalytics(): Promise<any> {
    const response = await this.client.get('/api/v1/users/analytics');
    return response.data;
  }

  // ============================================================================
  // WebSocket Connection (NEW)
  // ============================================================================

  createWebSocketConnection(projectId: string): WebSocket | null {
    if (typeof window === 'undefined') return null;
    
    const wsURL = this.baseURL.replace('http', 'ws');
    const token = this.getAuthToken();
    
    if (!token) return null;
    
    return new WebSocket(`${wsURL}/ws/projects/${projectId}?token=${token}`);
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const apiClient = new APIClient();
export default apiClient; 