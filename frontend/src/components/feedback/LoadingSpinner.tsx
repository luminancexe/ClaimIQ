import React from 'react';
import { cn } from '../../utils/format';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  className,
  label,
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  };

  return (
    <div className={cn('flex flex-col items-center justify-center p-6 space-y-3', className)}>
      <div
        className={cn(
          'border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin',
          sizeClasses[size]
        )}
      />
      {label && (
        <span className="text-xs font-mono text-slate-400 tracking-wider uppercase">
          {label}
        </span>
      )}
    </div>
  );
};
