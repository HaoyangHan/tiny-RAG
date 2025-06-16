/**
 * Header Component for TinyRAG v1.2
 * 
 * Provides the top navigation bar with branding, user menu, and global actions.
 *
 * @param {Object} props
 * @param {() => void} props.onMenuClick - Callback for menu button click.
 * @returns {JSX.Element}
 */

import React from 'react';
import { Bars3Icon } from '@heroicons/react/24/outline';

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm">
      <div className="flex items-center justify-between h-16 px-4">
        <button
          onClick={onMenuClick}
          className="p-2 rounded-md hover:bg-gray-100"
        >
          <Bars3Icon className="h-6 w-6" />
        </button>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              TinyRAG
            </h1>
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
              v1.2
            </span>
          </div>
        </div>
      </div>
    </header>
  );
} 