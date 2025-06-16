/**
 * Status bar for TinyRAG.
 *
 * Displays global status and indicators.
 *
 * @returns {JSX.Element}
 */
import React from 'react';

export function StatusBar() {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-100 border-t">
      <div className="container mx-auto px-4 py-2 flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Ready
        </div>
        <div className="text-sm text-gray-600">
          {/* Add status indicators here */}
        </div>
      </div>
    </div>
  );
} 