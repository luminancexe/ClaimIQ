import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { cn } from '../../utils/format';

interface ErrorAlertProps {
  title?: string;
  message: string;
  requestId?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  title = 'System Error',
  message,
  requestId,
  onRetry,
  className,
}) => {
  return (
    <div
      className={cn(
        'p-5 rounded-lg border border-rose-500/30 bg-rose-500/10 text-slate-200 space-y-3',
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <h4 className="font-semibold text-rose-300 text-sm tracking-wide">{title}</h4>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center space-x-1.5 px-3 py-1 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-xs font-medium text-rose-200 rounded transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
        )}
      </div>
      <p className="text-xs text-slate-300 pl-8 leading-relaxed">{message}</p>
      {requestId && (
        <div className="pl-8 text-[11px] font-mono text-slate-400">
          Request ID: <span className="text-cyan-400 select-all">{requestId}</span>
        </div>
      )}
    </div>
  );
};
