import React from 'react';
import { SEVERITY_MAP } from '../../constants/status';
import { cn } from '../../utils/format';

interface SeverityBadgeProps {
  severity: string;
  className?: string;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, className }) => {
  const config = SEVERITY_MAP[severity] || {
    label: severity,
    bgClass: 'bg-slate-800',
    textClass: 'text-slate-300',
    borderClass: 'border-slate-700',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border font-mono tracking-tight',
        config.bgClass,
        config.textClass,
        config.borderClass,
        className
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current" />
      {config.label}
    </span>
  );
};
