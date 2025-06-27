/**
 * TinyRAG v1.4.1 Authentication Store
 * 
 * Zustand store for managing authentication state,
 * user data, and auth-related actions.
 */

'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials, RegisterData } from '@/types';
import { api, APIError } from '@/services/api';

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login action
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        
        try {
          const authResponse = await api.login(credentials);
          
          // The login response only contains token info, need to fetch user data
          const user = await api.getCurrentUser();
          
          set({
            user: user,
            token: authResponse.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error) {
          const errorMessage = error instanceof APIError 
            ? error.message 
            : 'Login failed. Please try again.';
            
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage
          });
          
          throw error;
        }
      },

      // Register action
      register: async (userData: RegisterData) => {
        set({ isLoading: true, error: null });
        
        try {
          const user = await api.register(userData);
          
          // After successful registration, automatically log in
          await get().login({
            email: userData.email,
            password: userData.password
          });
        } catch (error) {
          const errorMessage = error instanceof APIError 
            ? error.message 
            : 'Registration failed. Please try again.';
            
          set({
            isLoading: false,
            error: errorMessage
          });
          
          throw error;
        }
      },

      // Logout action
      logout: async () => {
        set({ isLoading: true, error: null });
        
        try {
          await api.logout();
        } catch (error) {
          console.warn('Logout API call failed:', error);
        } finally {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        }
      },

      // Clear error action
      clearError: () => {
        set({ error: null });
      },

      // Initialize authentication from stored token
      initializeAuth: async () => {
        const { token } = get();
        
        if (!token) {
          set({ isLoading: false });
          return;
        }

        set({ isLoading: true, error: null });
        
        try {
          // Ensure API client has the token
          api.setToken(token);
          
          const user = await api.getCurrentUser();
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } catch (error) {
          // Token is invalid or expired
          console.warn('Auth initialization failed:', error);
          
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null
          });
        }
      },

      refreshUser: async () => {
        const { isAuthenticated } = get();
        
        if (!isAuthenticated) {
          return;
        }

        try {
          const user = await api.getCurrentUser();
          set({ user });
        } catch (error) {
          console.warn('Failed to refresh user data:', error);
          // Don't log out on refresh failure, just log the error
        }
      }
    }),
    {
      name: 'tinyrag-auth-store',
      partialize: (state) => ({ 
        token: state.token,
        user: state.user 
      }),
    }
  )
);

// Helper hook for checking specific permissions
export const useAuthPermissions = () => {
  const { user, isAuthenticated } = useAuthStore();
  
  return {
    canCreateProject: isAuthenticated,
    canUploadDocument: isAuthenticated,
    canCreateElement: isAuthenticated,
    canDeleteProject: (projectOwnerId: string) => 
      isAuthenticated && user?.id === projectOwnerId,
    canEditProject: (projectOwnerId: string, collaborators: string[]) => 
      isAuthenticated && (
        user?.id === projectOwnerId || 
        collaborators.includes(user?.id || '')
      ),
    isProjectOwner: (projectOwnerId: string) => 
      isAuthenticated && user?.id === projectOwnerId
  };
};

// Helper hook for auth actions without exposing the entire store
export const useAuth = () => {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    error, 
    login, 
    register, 
    logout, 
    clearError,
    initializeAuth,
    refreshUser
  } = useAuthStore();

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
    initializeAuth,
    refreshUser
  };
}; 