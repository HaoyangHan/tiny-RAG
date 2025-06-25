/**
 * TinyRAG v1.4.1 Authentication Store
 * 
 * Zustand store for managing authentication state,
 * user data, and auth-related actions.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials, RegisterData } from '@/types';
import { apiClient } from '@/services/api';

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
  logout: () => void;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
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
          // Mock implementation - replace with actual API call
          await new Promise(resolve => setTimeout(resolve, 1000));
          const mockUser: User = {
            id: '1',
            email: credentials.email,
            username: credentials.email.split('@')[0],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
          set({
            user: mockUser,
            token: 'mock-token',
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.message || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      // Register action
      register: async (userData: RegisterData) => {
        set({ isLoading: true, error: null });
        
        try {
          const authResponse = await apiClient.register(userData);
          
          set({
            user: authResponse.user,
            token: authResponse.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Registration failed',
          });
          throw error;
        }
      },

      // Logout action
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      // Clear error action
      clearError: () => {
        set({ error: null });
      },

      // Initialize authentication from stored token
      initializeAuth: async () => {
        const token = get().token;
        if (token) {
          set({ isAuthenticated: true });
        }
      },
    }),
    {
      name: 'tinyrag-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
); 