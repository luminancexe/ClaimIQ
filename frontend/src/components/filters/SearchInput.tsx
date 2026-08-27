import React from 'react';
import { Search, X } from 'lucide-react';
import { cn } from '../../utils/format';

interface SearchInputProps {
  value: string;
  onChange: (val: string) => void;
  onClear?: () => void;
  placeholder?: string;
  className?: string;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onChange,
  onClear,
  placeholder = 'Search...',
  className,
}) => {
  return (
    <div className={cn('relative flex items-center min-w-[220px]', className)}>
      <Search className="w-4 h-4 absolute left-3 text-slate-500 pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-surface-sidebar/80 border border-slate-700/80 hover:border-slate-600 focus:border-cyan-500 rounded-lg pl-9 pr-8 py-1.5 text-xs text-slate-200 placeholder-slate-500 font-mono transition focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
      />
      {value && onClear && (
        <button
          onClick={onClear}
          className="absolute right-2.5 text-slate-500 hover:text-slate-300 p-0.5 rounded"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};
