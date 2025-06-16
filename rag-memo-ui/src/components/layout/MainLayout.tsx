/**
 * Main Layout Component for TinyRAG v1.2
 * 
 * Provides the overall application layout with navigation, sidebar, and main content area.
 * Supports the new multi-format document processing and RAG framework features.
 */

import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StatusBar } from './StatusBar';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      
      <div className={cn(
        'flex flex-col min-h-screen transition-all duration-300',
        sidebarOpen ? 'ml-64' : 'ml-0'
      )}>
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        
        <main className="flex-1 container mx-auto px-4 py-8">
          {children}
        </main>
        
        <StatusBar />
      </div>
    </div>
  );
} 