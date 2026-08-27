import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { PlayCircle } from 'lucide-react';
import { getQARuns } from '../../api';
import { QARun, ColumnDef } from '../../types';

import { DataTable } from '../../components/tables/DataTable';
import { PaginationBar } from '../../components/tables/PaginationBar';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatNumber, formatDateTime } from '../../utils/format';

export const QARunsPage: React.FC = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);

  const [runs, setRuns] = useState<QARun[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [hasNext, setHasNext] = useState<boolean>(false);
  const [hasPrevious, setHasPrevious] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchRuns = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getQARuns({ page, page_size: pageSize });
      setRuns(res.items);
      setTotal(res.total);
      setTotalPages(res.total_pages);
      setHasNext(res.has_next);
      setHasPrevious(res.has_previous);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch QA execution runs';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize]);

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  const columns: ColumnDef<QARun>[] = [
    {
      key: 'run_reference',
      header: 'Run Reference',
      cell: (row) => (
        <span className="font-mono text-cyan-400 font-bold hover:underline">
          {row.run_reference}
        </span>
      ),
    },
    {
      key: 'batch_identifier',
      header: 'Batch ID',
      cell: (row) => <span className="font-mono text-slate-400 text-xs">{row.batch_identifier}</span>,
    },
    {
      key: 'started_at',
      header: 'Started At',
      cell: (row) => <span className="font-mono text-slate-300 text-xs">{formatDateTime(row.started_at)}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      cell: (row) => (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          {row.status}
        </span>
      ),
    },
    {
      key: 'total_rules_evaluated',
      header: 'Rules Evaluated',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-200">{row.total_rules_evaluated}</span>,
    },
    {
      key: 'total_records_evaluated',
      header: 'Records Evaluated',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-slate-200">{formatNumber(row.total_records_evaluated)}</span>
      ),
    },
    {
      key: 'total_issues_detected',
      header: 'Issues Found',
      align: 'right',
      cell: (row) => (
        <span className="font-mono font-bold text-rose-400">
          {formatNumber(row.total_issues_detected)}
        </span>
      ),
    },
    {
      key: 'dq_score',
      header: 'DQ Score',
      align: 'right',
      cell: (row) => {
        const scoreNum = parseFloat(row.dq_score || '100');
        return (
          <span
            className={`font-mono font-bold ${
              scoreNum >= 90 ? 'text-emerald-400' : scoreNum >= 75 ? 'text-amber-400' : 'text-rose-400'
            }`}
          >
            {row.dq_score ? `${scoreNum.toFixed(1)}/100` : '—'}
          </span>
        );
      },
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <PlayCircle className="w-5 h-5 text-cyan-400" />
            <span>QA Execution Runs</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Historical QA telemetry execution audit log and batch evaluation metrics.
          </p>
        </div>
      </div>

      {error && (
        <ErrorAlert
          title="Execution Runs Error"
          message={error.message}
          requestId={error.requestId}
          onRetry={fetchRuns}
        />
      )}

      <DataTable
        columns={columns}
        data={runs}
        keyExtractor={(r) => r.run_id}
        isLoading={isLoading}
        emptyTitle="No Execution Runs Recorded"
        emptyDescription="No QA engine execution runs were found in the telemetry tables."
        onRowClick={(row) => navigate(`/qa/runs/${row.run_id}`)}
      />

      <PaginationBar
        page={page}
        pageSize={pageSize}
        total={total}
        totalPages={totalPages}
        hasNext={hasNext}
        hasPrevious={hasPrevious}
        onPageChange={setPage}
        onPageSizeChange={(s) => {
          setPageSize(s);
          setPage(1);
        }}
      />
    </div>
  );
};
