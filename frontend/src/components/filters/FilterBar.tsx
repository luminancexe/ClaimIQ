import React, { ReactNode } from 'react';
import { RotateCcw } from 'lucide-react';
import { cn } from '../../utils/format';

interface FilterBarProps {
  children: ReactNode;
  onReset?: () => void;
  className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({ children, onReset, className }) => {
  return (
    <div
      className={cn(
        'flex flex-wrap items-center justify-between gap-3 p-3 bg-surface-card/80 border border-slate-800 rounded-xl mb-4 backdrop-blur-sm',
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-3 flex-1">{children}</div>
      {onReset && (
        <button
          onClick={onReset}
          title="Reset Filters"
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-mono transition"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>
      )}
    </div>
  );
};
