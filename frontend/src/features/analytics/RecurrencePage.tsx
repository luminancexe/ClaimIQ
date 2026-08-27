import React, { useState, useEffect } from 'react';
import { Repeat } from 'lucide-react';
import { getRecurrence } from '../../api';
import { RecurrenceResponse, RecurrencePattern, ColumnDef } from '../../types';
import { DataTable } from '../../components/tables/DataTable';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatNumber, formatDate, formatPercentage } from '../../utils/format';

export const RecurrencePage: React.FC = () => {
  const [recurrence, setRecurrence] = useState<RecurrenceResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchRecurrence = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getRecurrence();
      setRecurrence(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve recurrence patterns';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecurrence();
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Scanning Entity Defect Recurrence Clusters..." />;
  }

  if (error || !recurrence) {
    return (
      <ErrorAlert
        title="Recurrence Analytics Error"
        message={error?.message || 'Recurrence pattern data unavailable'}
        requestId={error?.requestId}
        onRetry={fetchRecurrence}
      />
    );
  }

  const columns: ColumnDef<RecurrencePattern>[] = [
    {
      key: 'recurrence_rank',
      header: 'Rank',
      cell: (row) => (
        <span className="font-mono font-bold text-cyan-400">
          #{row.recurrence_rank}
        </span>
      ),
    },
    {
      key: 'entity_type',
      header: 'Entity Type',
      cell: (row) => (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
          {row.entity_type}
        </span>
      ),
    },
    {
      key: 'entity_identifier',
      header: 'Entity ID',
      cell: (row) => (
        <span className="font-mono font-semibold text-slate-200">{row.entity_identifier}</span>
      ),
    },
    {
      key: 'anomaly_code',
      header: 'Anomaly Code',
      cell: (row) => (
        <span className="font-mono text-rose-400 font-bold">{row.anomaly_code}</span>
      ),
    },
    {
      key: 'occurrence_count',
      header: 'Occurrences',
      align: 'right',
      cell: (row) => (
        <span className="font-mono font-bold text-slate-100">
          {formatNumber(row.occurrence_count)}
        </span>
      ),
    },
    {
      key: 'first_detected_at',
      header: 'First Seen',
      cell: (row) => (
        <span className="font-mono text-slate-400 text-xs">{formatDate(row.first_detected_at)}</span>
      ),
    },
    {
      key: 'last_detected_at',
      header: 'Last Seen',
      cell: (row) => (
        <span className="font-mono text-slate-400 text-xs">{formatDate(row.last_detected_at)}</span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <Repeat className="w-5 h-5 text-cyan-400" />
            <span>Recurrence & Repeat Offender Clusters</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Pattern recognition detecting systemic repeating defect patterns across billing entities.
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
        <div className="p-5 bg-surface-card rounded-xl border border-slate-800 space-y-2">
          <span className="text-slate-400 uppercase">Repeating Defect Clusters</span>
          <div className="text-2xl font-bold text-cyan-400">
            {formatNumber(recurrence.recurring_cluster_count)}
          </div>
          <p className="text-[11px] text-slate-500">Identified multi-occurrence pattern groups</p>
        </div>

        <div className="p-5 bg-surface-card rounded-xl border border-slate-800 space-y-2">
          <span className="text-slate-400 uppercase">Repeat Issue Rate</span>
          <div className="text-2xl font-bold text-amber-400">
            {formatPercentage(recurrence.repeat_issue_rate, true)}
          </div>
          <p className="text-[11px] text-slate-500">Proportion of defects categorized as recurrent</p>
        </div>

        <div className="p-5 bg-surface-card rounded-xl border border-slate-800 space-y-2">
          <span className="text-slate-400 uppercase">Total Repeating Occurrences</span>
          <div className="text-2xl font-bold text-rose-400">
            {formatNumber(recurrence.total_repeating_occurrences)}
          </div>
          <p className="text-[11px] text-slate-500">Aggregated count of repeat defect events</p>
        </div>
      </div>

      {/* Recurrence Patterns Table */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-100 font-mono">
          Top Repeat Entity Defect Register
        </h2>
        <DataTable
          columns={columns}
          data={recurrence.top_repeat_entities}
          keyExtractor={(item) => `${item.entity_type}-${item.entity_identifier}-${item.anomaly_code}`}
          emptyTitle="No Recurrence Patterns Found"
          emptyDescription="No repeat defect clusters detected across the synthetic dataset."
        />
      </div>
    </div>
  );
};
