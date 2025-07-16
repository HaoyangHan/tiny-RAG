/**
 * TinyRAG v1.4.2 TypeScript Type Definitions
 * 
 * Comprehensive type definitions for the frontend application
 * following the API schema and UI/UX design requirements.
 * Updated to match backend model structure.
 */

// ============================================================================
// Authentication Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterData {
  email: string;
  password: string;
  username: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  role: string;
}

// ============================================================================
// Project Types
// ============================================================================

export enum TenantType {
  HR = "hr",
  CODING = "coding", 
  FINANCIAL_REPORT = "financial_report",
  DEEP_RESEARCH = "deep_research",
  QA_GENERATION = "qa_generation",
  RAW_RAG = "raw_rag"
}

export enum ProjectStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  ARCHIVED = "archived"
}

export enum VisibilityType {
  PRIVATE = "private",
  PUBLIC = "public",
  RESTRICTED = "restricted"
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  tenant_type: TenantType;
  keywords: string[];
  visibility: VisibilityType;
  status: ProjectStatus;
  owner_id: string;
  collaborators: string[];
  document_count: number;
  element_count: number;
  generation_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateRequest {
  name: string;
  description?: string;
  tenant_type: TenantType;
  keywords?: string[];
  visibility?: VisibilityType;
}

// ============================================================================
// Document Types (Updated to match backend model)
// ============================================================================

export enum DocumentStatus {
  UPLOADING = "uploading",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  ARCHIVED = "archived"
}

export interface Document {
  id: string;
  user_id: string;
  project_id: string;
  filename: string;
  content_type: string;
  file_size: number;
  status: DocumentStatus;
  chunk_count?: number;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

// ============================================================================
// Element Types (Updated to match backend model)
// ============================================================================

export enum ElementType {
  PROMPT_TEMPLATE = "prompt_template",
  MCP_CONFIG = "mcp_config",
  AGENTIC_TOOL = "agentic_tool",
  RAG_CONFIG = "rag_config"
}

export enum ElementStatus {
  DRAFT = "draft",
  ACTIVE = "active",
  DEPRECATED = "deprecated",
  ARCHIVED = "archived"
}

export interface Element {
  id: string;
  name: string;
  description?: string;
  project_id: string;
  tenant_type: TenantType;
  task_type: string;
  element_type: ElementType;
  status: ElementStatus;
  template: {
    content: string;
    variables: string[];
    execution_config: Record<string, any>;
    version: string;
    changelog: string[];
  };
  execution_history: string[];
  usage_statistics: Record<string, any>;
  tags: string[];
  owner_id: string;
  execution_count: number;
  created_at: string;
  updated_at: string;
}

export interface ElementDetail extends Element {
  template_content: string;
  template_variables: string[];
}

export interface ElementCreateRequest {
  name: string;
  description?: string;
  project_id: string;
  element_type: ElementType;
  template_content: string;
  additional_instructions_template?: string;
  execution_config?: Record<string, any>;
  tags?: string[];
}

// ============================================================================
// Generation Types
// ============================================================================

export enum GenerationStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled"
}

export interface Generation {
  id: string;
  element_id: string;
  project_id: string;
  status: GenerationStatus;
  model_used?: string;
  chunk_count: number;
  token_usage: number;
  created_at: string;
  updated_at: string;
  // Optional fields for enhanced responses
  content?: string;
  cost_usd?: number;
  generation_time_ms?: number;
  // Legacy fields for backward compatibility
  element_name?: string;
  additional_instructions?: string;
  source_chunks?: Array<Record<string, any>>;
  output_text?: string;
  tokens_used?: number; // Legacy - maps to token_usage
  execution_time?: number; // Legacy - maps to generation_time_ms
  cost?: number; // Legacy - maps to cost_usd
  error_message?: string;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

// ============================================================================
// Evaluation Types
// ============================================================================

export enum EvaluationStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

export interface Evaluation {
  id: string;
  generation_id: string;
  project_id: string;
  status: EvaluationStatus;
  overall_score?: number;
  criteria_scores?: Record<string, number>;
  evaluator_model?: string;
  hallucination_detected: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Bulk Execution Types
// ============================================================================

export interface BulkExecutionStatus {
  execution_id: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  total_elements: number;
  completed_elements: number;
  failed_elements: number;
  progress_percentage: number;
  estimated_completion?: string;
  element_statuses: ElementExecutionStatus[];
}

export interface ElementExecutionStatus {
  element_id: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  generation_id?: string;
  error_message?: string;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface UIState {
  sidebarCollapsed: boolean;
  currentProject?: string;
  theme: "light" | "dark";
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface APIResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface APIError {
  status: number;
  message: string;
  details?: Record<string, any>;
}

// ============================================================================
// Template Validation Types
// ============================================================================

export interface TemplateValidationRequest {
  template_content: string;
  variables: string[];
  element_type: ElementType;
}

export interface TemplateValidationResponse {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  extracted_variables: string[];
  suggestions: string[];
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface UserAnalytics {
  total_projects: number;
  total_documents: number;
  total_elements: number;
  total_generations: number;
  total_evaluations: number;
  monthly_usage: MonthlyUsage[];
  cost_breakdown: CostBreakdown;
  recent_activity: ActivityItem[];
}

export interface MonthlyUsage {
  month: string;
  generations: number;
  cost_usd: number;
  tokens_used: number;
}

export interface CostBreakdown {
  total_cost_usd: number;
  by_model: Record<string, number>;
  by_project: Record<string, number>;
}

export interface ActivityItem {
  id: string;
  type: "document_upload" | "element_created" | "generation_completed" | "evaluation_created";
  description: string;
  project_name: string;
  timestamp: string;
}

// ============================================================================
// Form Types
// ============================================================================

export interface FormFieldError {
  field: string;
  message: string;
}

export interface FormState<T> {
  data: T;
  errors: FormFieldError[];
  isSubmitting: boolean;
  isValid: boolean;
}

// ============================================================================
// Filter and Search Types
// ============================================================================

export interface ProjectFilters {
  tenant_type?: TenantType;
  status?: ProjectStatus;
  visibility?: VisibilityType;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface ElementFilters {
  project_id?: string;
  element_type?: ElementType;
  status?: ElementStatus;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface GenerationFilters {
  project_id?: string;
  element_id?: string;
  status?: GenerationStatus;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
} 