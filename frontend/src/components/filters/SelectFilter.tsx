import React from 'react';
import { cn } from '../../utils/format';

interface SelectOption {
  label: string;
  value: string;
}

interface SelectFilterProps {
  label?: string;
  value: string;
  onChange: (val: string) => void;
  options: SelectOption[];
  allLabel?: string;
  className?: string;
}

export const SelectFilter: React.FC<SelectFilterProps> = ({
  label,
  value,
  onChange,
  options,
  allLabel = 'All',
  className,
}) => {
  return (
    <div className={cn('flex items-center space-x-2', className)}>
      {label && <span className="text-xs text-slate-400 font-mono">{label}:</span>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-surface-sidebar/80 border border-slate-700/80 hover:border-slate-600 focus:border-cyan-500 rounded-lg px-3 py-1.5 text-xs text-slate-200 font-mono transition focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
      >
        <option value="">{allLabel}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};
