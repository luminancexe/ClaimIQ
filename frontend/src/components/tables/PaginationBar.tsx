import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { cn, formatNumber } from '../../utils/format';

interface PaginationBarProps {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
  onPageChange: (newPage: number) => void;
  onPageSizeChange?: (newSize: number) => void;
  pageSizeOptions?: number[];
  className?: string;
}

export const PaginationBar: React.FC<PaginationBarProps> = ({
  page,
  pageSize,
  total,
  totalPages,
  hasNext,
  hasPrevious,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 25, 50, 100],
  className,
}) => {
  const startItem = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, total);

  return (
    <div
      className={cn(
        'flex flex-col sm:flex-row items-center justify-between gap-3 px-4 py-3 bg-surface-card/60 border-t border-slate-800 text-xs text-slate-400 font-mono',
        className
      )}
    >
      <div className="flex items-center space-x-4">
        <span>
          Showing <strong className="text-slate-200">{formatNumber(startItem)}</strong>–
          <strong className="text-slate-200">{formatNumber(endItem)}</strong> of{' '}
          <strong className="text-cyan-400">{formatNumber(total)}</strong> records
        </span>

        {onPageSizeChange && (
          <div className="flex items-center space-x-1.5 pl-2 border-l border-slate-800">
            <span>Show:</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              aria-label="Rows per page"
              className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-2 py-0.5 text-xs focus:outline-none focus:border-cyan-500"
            >
              {pageSizeOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-1">
        <span className="mr-3 text-slate-400">
          Page <strong className="text-slate-200">{page}</strong> of{' '}
          <strong className="text-slate-200">{totalPages || 1}</strong>
        </span>

        <button
          onClick={() => onPageChange(1)}
          disabled={!hasPrevious || page === 1}
          aria-label="First page"
          className="p-1 rounded bg-slate-800/80 border border-slate-700 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800/80 transition"
        >
          <ChevronsLeft className="w-4 h-4" />
        </button>
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!hasPrevious}
          aria-label="Previous page"
          className="p-1 rounded bg-slate-800/80 border border-slate-700 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800/80 transition"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!hasNext}
          aria-label="Next page"
          className="p-1 rounded bg-slate-800/80 border border-slate-700 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800/80 transition"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={!hasNext || page === totalPages}
          aria-label="Last page"
          className="p-1 rounded bg-slate-800/80 border border-slate-700 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800/80 transition"
        >
          <ChevronsRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
