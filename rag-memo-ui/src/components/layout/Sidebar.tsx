import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <div
      className={cn(
        'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}
    >
      <div className="flex flex-col h-full">
        <div className="p-4 border-b">
          <h2 className="text-xl font-semibold">RAG Memo</h2>
        </div>
        
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            <li>
              <Link
                href="/"
                className="block px-4 py-2 rounded-lg hover:bg-gray-100"
              >
                Home
              </Link>
            </li>
            <li>
              <Link
                href="/documents"
                className="block px-4 py-2 rounded-lg hover:bg-gray-100"
              >
                Documents
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  );
} 