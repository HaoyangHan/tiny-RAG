import React from 'react';

interface StatusBadgeProps {
  status: string;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  variant = 'default',
  size = 'md',
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-sm',
    lg: 'px-3 py-1 text-base'
  };

  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800'
  };

  // Auto-detect variant based on status if not specified
  const getVariantFromStatus = (statusText: string): keyof typeof variantClasses => {
    const lowerStatus = statusText.toLowerCase();
    
    if (lowerStatus.includes('active') || lowerStatus.includes('completed') || lowerStatus.includes('success')) {
      return 'success';
    }
    if (lowerStatus.includes('processing') || lowerStatus.includes('pending')) {
      return 'info';
    }
    if (lowerStatus.includes('warning') || lowerStatus.includes('draft')) {
      return 'warning';
    }
    if (lowerStatus.includes('failed') || lowerStatus.includes('error') || lowerStatus.includes('archived')) {
      return 'error';
    }
    return 'default';
  };

  const finalVariant = variant === 'default' ? getVariantFromStatus(status) : variant;

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClasses[size]} ${variantClasses[finalVariant]} ${className}`}
    >
      {status}
    </span>
  );
}; 