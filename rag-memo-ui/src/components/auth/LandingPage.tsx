/**
 * TinyRAG v1.4.1 Landing Page Component
 * 
 * Split-screen landing page with brand section and authentication forms
 * following the UI/UX design specifications.
 */

'use client';

import { useState } from 'react';
import { CpuChipIcon } from '@heroicons/react/24/outline';
import { LoginForm } from './LoginForm';

interface LandingPageProps {
  onAuthSuccess?: () => void;
}

export function LandingPage({ onAuthSuccess }: LandingPageProps) {
  return (
    <div className="min-h-screen flex">
      {/* Left Side - Brand */}
      <div className="flex-1 bg-gradient-to-br from-blue-600 to-purple-800 flex items-center justify-center">
        <div className="text-center text-white px-12">
          <div className="flex items-center justify-center mb-8">
            <CpuChipIcon className="w-16 h-16 mr-4" />
            <h1 className="text-5xl font-bold">TinyRAG</h1>
          </div>
          <p className="text-xl text-blue-100 leading-relaxed max-w-md">
            The complete RAG platform for intelligent document processing, 
            AI generation workflows, and quality evaluation.
          </p>
        </div>
      </div>

      {/* Right Side - Authentication */}
      <div className="flex-1 bg-white flex items-center justify-center px-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome back</h2>
            <p className="text-gray-600">Sign in to access your RAG workflows</p>
          </div>
          
          <LoginForm onSuccess={onAuthSuccess} />
        </div>
      </div>
    </div>
  );
} 