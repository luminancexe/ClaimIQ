import React, { ReactNode } from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { cn } from '../../utils/format';

interface MetricCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendText?: string;
  icon?: ReactNode;
  variant?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'indigo' | 'default';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subValue,
  trend,
  trendText,
  icon,
  variant = 'default',
  className,
}) => {
  const variantStyles = {
    cyan: 'border-cyan-500/30 hover:border-cyan-500/50 group-hover:text-cyan-400',
    emerald: 'border-emerald-500/30 hover:border-emerald-500/50 group-hover:text-emerald-400',
    amber: 'border-amber-500/30 hover:border-amber-500/50 group-hover:text-amber-400',
    rose: 'border-rose-500/30 hover:border-rose-500/50 group-hover:text-rose-400',
    indigo: 'border-indigo-500/30 hover:border-indigo-500/50 group-hover:text-indigo-400',
    default: 'border-slate-800 hover:border-slate-700',
  };

  const glowStyles = {
    cyan: 'shadow-[0_0_20px_-8px_rgba(6,182,212,0.15)]',
    emerald: 'shadow-[0_0_20px_-8px_rgba(16,185,129,0.15)]',
    amber: 'shadow-[0_0_20px_-8px_rgba(245,158,11,0.15)]',
    rose: 'shadow-[0_0_20px_-8px_rgba(244,63,94,0.15)]',
    indigo: 'shadow-[0_0_20px_-8px_rgba(99,102,241,0.15)]',
    default: '',
  };

  return (
    <div
      className={cn(
        'group relative bg-surface-card/90 rounded-xl p-5 border transition-all duration-200 backdrop-blur-sm',
        variantStyles[variant],
        glowStyles[variant],
        className
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {icon && (
          <div className="text-slate-400 group-hover:text-slate-200 transition">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-baseline space-x-2">
        <div className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {value}
        </div>
        {subValue && (
          <span className="text-xs font-mono text-slate-400">{subValue}</span>
        )}
      </div>

      {(trend || trendText) && (
        <div className="mt-3 flex items-center space-x-1.5 text-xs">
          {trend === 'up' && <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />}
          {trend === 'down' && <ArrowDownRight className="w-3.5 h-3.5 text-rose-400" />}
          {trend === 'neutral' && <Minus className="w-3.5 h-3.5 text-slate-400" />}
          <span
            className={cn(
              'font-medium text-[11px]',
              trend === 'up' && 'text-emerald-400',
              trend === 'down' && 'text-rose-400',
              trend === 'neutral' && 'text-slate-400'
            )}
          >
            {trendText}
          </span>
        </div>
      )}
    </div>
  );
};
