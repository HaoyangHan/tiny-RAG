/**
 * Enhanced API client for TinyRAG v1.4.1
 * Provides comprehensive API integration with error handling, retry logic, and authentication
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User, 
  Project, 
  Document, 
  Element, 
  Generation, 
  Evaluation,
  PaginatedResponse 
} from '@/types';

export class APIError extends Error {
  public status: number;
  public details?: Record<string, any>;

  constructor(status: number, message: string, details?: Record<string, any>) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.details = details;
  }
}

export interface APIConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

export class APIClient {
  private axiosInstance: AxiosInstance;
  private config: APIConfig;
  private token: string | null = null;
  
  constructor(config?: Partial<APIConfig>) {
    this.config = {
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000,
      ...config
    };

    this.axiosInstance = axios.create({
      baseURL: this.config.baseURL,
      timeout: this.config.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
    this.loadTokenFromStorage();
  }

  private setupInterceptors(): void {
    // Request interceptor for adding auth token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for handling errors and retries
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken();
          window.location.href = '/';
          return Promise.reject(new APIError(401, 'Authentication required'));
        }

        // Retry logic for network errors
        if (this.shouldRetry(error)) {
          return this.retryRequest(error);
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private shouldRetry(error: AxiosError): boolean {
    if (!error.config || (error.config as any).__retryCount >= this.config.retryAttempts) {
      return false;
    }

    // Retry on network errors or 5xx status codes
    return !error.response || (error.response.status >= 500 && error.response.status < 600);
  }

  private async retryRequest(error: AxiosError): Promise<AxiosResponse> {
    const config = error.config as any;
    config.__retryCount = (config.__retryCount || 0) + 1;

    await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * config.__retryCount));

    return this.axiosInstance.request(config);
  }

  private handleError(error: AxiosError): APIError {
    if (error.response) {
      const responseData = error.response.data as any;
      const message = responseData?.detail || responseData?.message || 'Request failed';
      return new APIError(error.response.status, message, responseData);
    } else if (error.request) {
      return new APIError(0, 'Network error - please check your connection');
    } else {
      return new APIError(0, 'Request configuration error');
    }
  }

  private loadTokenFromStorage(): void {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  private saveTokenToStorage(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  private clearToken(): void {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Public method to set token (for auth store synchronization)
  setToken(token: string | null): void {
    this.token = token;
    if (token) {
      this.saveTokenToStorage(token);
    } else {
      this.clearToken();
    }
  }

  // Authentication endpoints
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await this.axiosInstance.post<AuthResponse>('/api/v1/auth/login', {
        identifier: credentials.email, // API uses 'identifier' field
        password: credentials.password
      });
      
      this.token = response.data.access_token;
      this.saveTokenToStorage(this.token);
      
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async register(userData: RegisterData): Promise<User> {
    try {
      const response = await this.axiosInstance.post<User>('/api/v1/auth/register', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await this.axiosInstance.get<User>('/api/v1/auth/me');
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async logout(): Promise<void> {
    try {
      await this.axiosInstance.post('/api/v1/auth/logout');
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      this.clearToken();
    }
  }

  // Health check endpoint
  async checkHealth(): Promise<{ status: string; llm_provider?: string }> {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Project endpoints
  async getProjects(params?: {
    page?: number;
    page_size?: number;
    tenant_type?: string;
    status?: string;
    visibility?: string;
    search?: string;
  }): Promise<PaginatedResponse<Project>> {
    try {
      const response = await this.axiosInstance.get<PaginatedResponse<Project>>('/api/v1/projects/', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async getProject(projectId: string): Promise<Project> {
    try {
      const response = await this.axiosInstance.get<Project>(`/api/v1/projects/${projectId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async createProject(projectData: Partial<Project>): Promise<Project> {
    try {
      const response = await this.axiosInstance.post<Project>('/api/v1/projects/', projectData);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async updateProject(projectId: string, updates: Partial<Project>): Promise<Project> {
    try {
      const response = await this.axiosInstance.put<Project>(`/api/v1/projects/${projectId}`, updates);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async deleteProject(projectId: string): Promise<void> {
    try {
      await this.axiosInstance.delete(`/api/v1/projects/${projectId}`);
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Bulk element execution
  async executeAllElements(projectId: string, options?: { element_ids?: string[] }): Promise<{ execution_id: string }> {
    try {
      const response = await this.axiosInstance.post(`/api/v1/projects/${projectId}/elements/execute-all`, options);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async getBulkExecutionStatus(projectId: string, executionId: string): Promise<{
    execution_id: string;
    status: string;
    total_elements: number;
    completed_elements: number;
    failed_elements: number;
    progress_percentage: number;
    estimated_completion?: string;
    element_statuses: Array<{ element_id: string; status: string; error?: string }>;
  }> {
    try {
      const response = await this.axiosInstance.get(
        `/api/v1/projects/${projectId}/elements/execute-all-status`,
        { params: { execution_id: executionId } }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Document endpoints
  async uploadDocument(file: File, projectId?: string): Promise<Document> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const params = projectId ? { project_id: projectId } : {};
      
      const response = await this.axiosInstance.post<Document>('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        params
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async getDocuments(params?: {
    project_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Document>> {
    try {
      const response = await this.axiosInstance.get<PaginatedResponse<Document>>('/api/v1/documents', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async getDocument(documentId: string): Promise<Document> {
    try {
      const response = await this.axiosInstance.get<Document>(`/api/v1/documents/${documentId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async deleteDocument(documentId: string): Promise<void> {
    try {
      await this.axiosInstance.delete(`/api/v1/documents/${documentId}`);
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Element endpoints
  async getElements(params?: {
    project_id?: string;
    element_type?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Element>> {
    try {
      const response = await this.axiosInstance.get<PaginatedResponse<Element>>('/api/v1/elements', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async createElement(elementData: Partial<Element>): Promise<Element> {
    try {
      const response = await this.axiosInstance.post<Element>('/api/v1/elements', elementData);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async getElement(elementId: string): Promise<Element> {
    try {
      const response = await this.axiosInstance.get<Element>(`/api/v1/elements/${elementId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async deleteElement(elementId: string): Promise<void> {
    try {
      await this.axiosInstance.delete(`/api/v1/elements/${elementId}`);
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async executeElement(elementId: string, variables: Record<string, any>): Promise<Generation> {
    try {
      const response = await this.axiosInstance.post<Generation>(`/api/v1/elements/${elementId}/execute`, variables);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async validateTemplate(templateData: {
    template_content: string;
    variables?: string[];
    element_type: string;
  }): Promise<{
    is_valid: boolean;
    errors: string[];
    warnings: string[];
    extracted_variables: string[];
    suggestions: string[];
  }> {
    try {
      const response = await this.axiosInstance.post('/api/v1/elements/validate-template', templateData);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Generation endpoints
  async getGenerations(params?: {
    project_id?: string;
    element_id?: string;
    execution_id?: string;
    status?: string;
    include_content?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Generation>> {
    try {
      console.log('API Client - getGenerations called with params:', params);
      console.log('API Client - current token:', this.token ? 'Token exists' : 'No token');
      console.log('API Client - Authorization header:', this.axiosInstance.defaults.headers.Authorization);
      
      const response = await this.axiosInstance.get<PaginatedResponse<Generation>>('/api/v1/generations', { params });
      console.log('API Client - getGenerations response:', response.data);
      return response.data;
    } catch (error) {
      console.error('API Client - getGenerations error:', error);
      throw this.handleError(error as AxiosError);
    }
  }

  async getGeneration(generationId: string): Promise<Generation> {
    try {
      const response = await this.axiosInstance.get<Generation>(`/api/v1/generations/${generationId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // Evaluation endpoints
  async getEvaluations(params?: {
    project_id?: string;
    generation_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Evaluation>> {
    try {
      const response = await this.axiosInstance.get<PaginatedResponse<Evaluation>>('/api/v1/evaluations', { params });
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  async createEvaluation(evaluationData: Partial<Evaluation>): Promise<Evaluation> {
    try {
      const response = await this.axiosInstance.post<Evaluation>('/api/v1/evaluations', evaluationData);
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }

  // User analytics
  async getUserAnalytics(): Promise<{
    total_projects: number;
    total_documents: number;
    total_elements: number;
    total_generations: number;
    total_cost: number;
    recent_activity: Array<{
      type: string;
      description: string;
      timestamp: string;
    }>;
  }> {
    try {
      const response = await this.axiosInstance.get('/api/v1/users/analytics');
      return response.data;
    } catch (error) {
      throw this.handleError(error as AxiosError);
    }
  }
}

// Export singleton instance
export const api = new APIClient(); 