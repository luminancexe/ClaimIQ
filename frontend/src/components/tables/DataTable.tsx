import React, { ReactNode } from 'react';
import { ColumnDef } from '../../types';
import { TableSkeleton } from '../feedback/Skeleton';
import { EmptyState } from '../feedback/EmptyState';
import { cn } from '../../utils/format';

export type { ColumnDef };


interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  keyExtractor: (row: T, index: number) => string | number;
  isLoading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  onRowClick?: (row: T) => void;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  isLoading = false,
  emptyTitle,
  emptyDescription,
  onRowClick,
  className,
}: DataTableProps<T>): React.ReactElement {
  if (isLoading) {
    return (
      <div className={cn('bg-surface-card rounded-xl border border-slate-800 overflow-hidden', className)}>
        <TableSkeleton rows={8} cols={columns.length} />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className={cn('bg-surface-card rounded-xl border border-slate-800 overflow-hidden p-6', className)}>
        <EmptyState title={emptyTitle} description={emptyDescription} />
      </div>
    );
  }

  return (
    <div className={cn('bg-surface-card rounded-xl border border-slate-800 overflow-hidden shadow-sm', className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-surface-sidebar/90 border-b border-slate-800 text-slate-400 font-mono uppercase tracking-wider text-[11px]">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    'px-4 py-3 font-semibold whitespace-nowrap',
                    col.align === 'right' && 'text-right',
                    col.align === 'center' && 'text-center',
                    col.headerClassName
                  )}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {data.map((row, idx) => {
              const rowKey = keyExtractor(row, idx);
              return (
                <tr
                  key={rowKey}
                  onClick={() => onRowClick && onRowClick(row)}
                  className={cn(
                    'transition-colors duration-150',
                    onRowClick ? 'cursor-pointer hover:bg-slate-800/40 active:bg-slate-800/60' : 'hover:bg-slate-800/20'
                  )}
                >
                  {columns.map((col) => (
                    <td
                      key={`${rowKey}-${col.key}`}
                      className={cn(
                        'px-4 py-3 text-slate-300 align-middle',
                        col.align === 'right' && 'text-right',
                        col.align === 'center' && 'text-center',
                        col.className
                      )}
                    >
                      {col.cell ? col.cell(row, idx) : (row as Record<string, unknown>)[col.key] as ReactNode}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
