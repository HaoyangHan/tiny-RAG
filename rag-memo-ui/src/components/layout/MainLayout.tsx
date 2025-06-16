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
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <Header 
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
      />

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar */}
        <Sidebar 
          open={sidebarOpen}
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main Content */}
        <main 
          className={cn(
            "flex-1 overflow-hidden transition-all duration-300",
            sidebarOpen && !sidebarCollapsed ? "ml-64" : sidebarOpen ? "ml-16" : "ml-0"
          )}
        >
          <div className="h-full flex flex-col">
            {/* Content Area */}
            <div className="flex-1 overflow-auto p-6">
              {children}
            </div>

            {/* Status Bar */}
            <StatusBar />
          </div>
        </main>
      </div>
    </div>
  );
} 