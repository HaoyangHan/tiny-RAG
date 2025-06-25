/**
 * Environment configuration for TinyRAG v1.4.1
 * Centralizes all environment variables and provides defaults
 */

export interface EnvironmentConfig {
  // API Configuration
  API_URL: string;
  WS_URL: string;
  
  // Application Configuration
  APP_NAME: string;
  APP_VERSION: string;
  NODE_ENV: string;
  
  // Feature Flags
  ENABLE_WEBSOCKETS: boolean;
  ENABLE_ANALYTICS: boolean;
  ENABLE_DEBUG_MODE: boolean;
  
  // Authentication Configuration
  TOKEN_STORAGE_KEY: string;
  SESSION_TIMEOUT: number; // in milliseconds
  
  // API Configuration
  API_TIMEOUT: number;
  API_RETRY_ATTEMPTS: number;
  API_RETRY_DELAY: number;
  
  // WebSocket Configuration
  WS_RECONNECT_INTERVAL: number;
  WS_MAX_RECONNECT_ATTEMPTS: number;
  
  // Upload Configuration
  MAX_FILE_SIZE: number; // in bytes
  ALLOWED_FILE_TYPES: string[];
  
  // UI Configuration
  DEFAULT_PAGE_SIZE: number;
  ANIMATION_DURATION: number;
}

const createEnvironmentConfig = (): EnvironmentConfig => {
  const isDevelopment = process.env.NODE_ENV === 'development';
  const isProduction = process.env.NODE_ENV === 'production';
  
  return {
    // API Configuration
    API_URL: process.env.NEXT_PUBLIC_API_URL || (isDevelopment ? 'http://localhost:8000' : 'https://api.tinyrag.com'),
    WS_URL: process.env.NEXT_PUBLIC_WS_URL || (isDevelopment ? 'ws://localhost:8000' : 'wss://api.tinyrag.com'),
    
    // Application Configuration
    APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'TinyRAG',
    APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION || '1.4.1',
    NODE_ENV: process.env.NODE_ENV || 'development',
    
    // Feature Flags
    ENABLE_WEBSOCKETS: process.env.NEXT_PUBLIC_ENABLE_WEBSOCKETS === 'true' || isDevelopment,
    ENABLE_ANALYTICS: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true' || isProduction,
    ENABLE_DEBUG_MODE: process.env.NEXT_PUBLIC_ENABLE_DEBUG === 'true' || isDevelopment,
    
    // Authentication Configuration
    TOKEN_STORAGE_KEY: 'tinyrag_auth_token',
    SESSION_TIMEOUT: parseInt(process.env.NEXT_PUBLIC_SESSION_TIMEOUT || '28800000'), // 8 hours
    
    // API Configuration
    API_TIMEOUT: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000'), // 30 seconds
    API_RETRY_ATTEMPTS: parseInt(process.env.NEXT_PUBLIC_API_RETRY_ATTEMPTS || '3'),
    API_RETRY_DELAY: parseInt(process.env.NEXT_PUBLIC_API_RETRY_DELAY || '1000'), // 1 second
    
    // WebSocket Configuration
    WS_RECONNECT_INTERVAL: parseInt(process.env.NEXT_PUBLIC_WS_RECONNECT_INTERVAL || '5000'), // 5 seconds
    WS_MAX_RECONNECT_ATTEMPTS: parseInt(process.env.NEXT_PUBLIC_WS_MAX_RECONNECT || '5'),
    
    // Upload Configuration
    MAX_FILE_SIZE: parseInt(process.env.NEXT_PUBLIC_MAX_FILE_SIZE || '10485760'), // 10MB
    ALLOWED_FILE_TYPES: (process.env.NEXT_PUBLIC_ALLOWED_FILE_TYPES || 'pdf,docx,txt,md,html').split(','),
    
    // UI Configuration
    DEFAULT_PAGE_SIZE: parseInt(process.env.NEXT_PUBLIC_DEFAULT_PAGE_SIZE || '20'),
    ANIMATION_DURATION: parseInt(process.env.NEXT_PUBLIC_ANIMATION_DURATION || '200'), // 200ms
  };
};

export const env = createEnvironmentConfig();

// Helper functions for environment checks
export const isDevelopment = () => env.NODE_ENV === 'development';
export const isProduction = () => env.NODE_ENV === 'production';
export const isTest = () => env.NODE_ENV === 'test';

// Validation function to ensure required environment variables are set
export const validateEnvironment = (): void => {
  const requiredVars = [
    'API_URL',
    'WS_URL',
    'APP_NAME',
    'APP_VERSION'
  ];

  const missingVars = requiredVars.filter(varName => {
    const value = env[varName as keyof EnvironmentConfig];
    return !value || (typeof value === 'string' && value.trim() === '');
  });

  if (missingVars.length > 0) {
    throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
  }

  // Validate URLs
  try {
    new URL(env.API_URL);
  } catch {
    throw new Error(`Invalid API_URL: ${env.API_URL}`);
  }

  // Validate numeric values
  if (env.API_TIMEOUT <= 0) {
    throw new Error('API_TIMEOUT must be greater than 0');
  }

  if (env.MAX_FILE_SIZE <= 0) {
    throw new Error('MAX_FILE_SIZE must be greater than 0');
  }

  if (env.DEFAULT_PAGE_SIZE <= 0) {
    throw new Error('DEFAULT_PAGE_SIZE must be greater than 0');
  }
};

// API endpoint configuration
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    LOGOUT: '/api/v1/auth/logout',
    ME: '/api/v1/auth/me',
    REFRESH: '/api/v1/auth/refresh'
  },
  
  // Projects
  PROJECTS: {
    LIST: '/api/v1/projects',
    CREATE: '/api/v1/projects',
    GET: (id: string) => `/api/v1/projects/${id}`,
    UPDATE: (id: string) => `/api/v1/projects/${id}`,
    DELETE: (id: string) => `/api/v1/projects/${id}`,
    EXECUTE_ALL: (id: string) => `/api/v1/projects/${id}/elements/execute-all`,
    EXECUTION_STATUS: (id: string) => `/api/v1/projects/${id}/elements/execute-all-status`,
    COLLABORATORS: (id: string) => `/api/v1/projects/${id}/collaborators`
  },
  
  // Documents
  DOCUMENTS: {
    LIST: '/api/v1/documents',
    UPLOAD: '/api/v1/documents/upload',
    GET: (id: string) => `/api/v1/documents/${id}`,
    DELETE: (id: string) => `/api/v1/documents/${id}`
  },
  
  // Elements
  ELEMENTS: {
    LIST: '/api/v1/elements',
    CREATE: '/api/v1/elements',
    GET: (id: string) => `/api/v1/elements/${id}`,
    UPDATE: (id: string) => `/api/v1/elements/${id}`,
    DELETE: (id: string) => `/api/v1/elements/${id}`,
    EXECUTE: (id: string) => `/api/v1/elements/${id}/execute`,
    VALIDATE_TEMPLATE: '/api/v1/elements/validate-template'
  },
  
  // Generations
  GENERATIONS: {
    LIST: '/api/v1/generations',
    GET: (id: string) => `/api/v1/generations/${id}`,
    DELETE: (id: string) => `/api/v1/generations/${id}`
  },
  
  // Evaluations
  EVALUATIONS: {
    LIST: '/api/v1/evaluations',
    CREATE: '/api/v1/evaluations',
    GET: (id: string) => `/api/v1/evaluations/${id}`,
    UPDATE: (id: string) => `/api/v1/evaluations/${id}`,
    DELETE: (id: string) => `/api/v1/evaluations/${id}`
  },
  
  // Users
  USERS: {
    ANALYTICS: '/api/v1/users/analytics',
    PROFILE: '/api/v1/users/profile'
  },
  
  // Health
  HEALTH: '/health'
};

// WebSocket endpoint configuration
export const WS_ENDPOINTS = {
  GLOBAL: '/ws',
  PROJECT: (id: string) => `/ws/projects/${id}`,
  USER: (id: string) => `/ws/users/${id}`
};

export default env; 