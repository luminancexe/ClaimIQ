import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Clock, Award } from 'lucide-react';
import { getQARunById, getQAResults, getDQScores } from '../../api';
import { QARun, QAResult, DQScoreSummary, ColumnDef } from '../../types';

import { DataTable } from '../../components/tables/DataTable';
import { DimensionBarChart } from '../../components/charts/DimensionBarChart';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatNumber, formatDateTime } from '../../utils/format';

export const QARunDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<QARun | null>(null);
  const [results, setResults] = useState<QAResult[]>([]);
  const [scores, setScores] = useState<DQScoreSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchRunData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const runIdNum = parseInt(id, 10);
        const [runData, resultsData, scoresData] = await Promise.all([
          getQARunById(id),
          getQAResults(runIdNum),
          getDQScores(runIdNum),
        ]);
        setRun(runData);
        setResults(resultsData);
        setScores(scoresData);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to fetch QA run telemetry';
        const reqId = (err as { requestId?: string })?.requestId;
        setError({ message: msg, requestId: reqId });
      } finally {
        setIsLoading(false);
      }
    };

    fetchRunData();
  }, [id]);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Retrieving QA Execution Run Artifacts..." />;
  }

  if (error || !run) {
    return (
      <div className="space-y-4">
        <Link
          to="/qa/runs"
          className="inline-flex items-center space-x-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Runs</span>
        </Link>
        <ErrorAlert
          title="Run Retrieval Error"
          message={error?.message || 'Run not found'}
          requestId={error?.requestId}
        />
      </div>
    );
  }

  const resultColumns: ColumnDef<QAResult>[] = [
    {
      key: 'rule_code',
      header: 'Rule Code',
      cell: (row) => (
        <span className="font-mono text-cyan-400 font-bold">
          {row.rule_code || `RULE-${row.rule_id}`}
        </span>
      ),
    },
    {
      key: 'records_evaluated',
      header: 'Records Evaluated',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-200">{formatNumber(row.records_evaluated)}</span>,
    },
    {
      key: 'issues_detected',
      header: 'Issues Detected',
      align: 'right',
      cell: (row) => (
        <span
          className={`font-mono font-bold ${
            row.issues_detected > 0 ? 'text-rose-400' : 'text-emerald-400'
          }`}
        >
          {formatNumber(row.issues_detected)}
        </span>
      ),
    },
    {
      key: 'execution_duration_ms',
      header: 'Execution Time',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-400">{row.execution_duration_ms} ms</span>,
    },
    {
      key: 'run_status',
      header: 'Status',
      cell: (row) => (
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono border ${
            row.run_status === 'COMPLETED'
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
          }`}
        >
          {row.run_status}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <Link
            to="/qa/runs"
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold font-mono text-cyan-400 tracking-tight">
                {run.run_reference}
              </h1>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                {run.status}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Batch: {run.batch_identifier} &bull; Started: {formatDateTime(run.started_at)}
            </p>
          </div>
        </div>
      </div>

      {/* Summary KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
        <div className="p-4 bg-surface-card rounded-xl border border-slate-800">
          <span className="text-slate-400 block mb-1">Rules Evaluated</span>
          <span className="text-xl font-bold text-slate-100">{run.total_rules_evaluated}</span>
        </div>
        <div className="p-4 bg-surface-card rounded-xl border border-slate-800">
          <span className="text-slate-400 block mb-1">Records Evaluated</span>
          <span className="text-xl font-bold text-cyan-400">{formatNumber(run.total_records_evaluated)}</span>
        </div>
        <div className="p-4 bg-surface-card rounded-xl border border-slate-800">
          <span className="text-slate-400 block mb-1">Issues Detected</span>
          <span className="text-xl font-bold text-rose-400">{formatNumber(run.total_issues_detected)}</span>
        </div>
        <div className="p-4 bg-surface-card rounded-xl border border-slate-800">
          <span className="text-slate-400 block mb-1">Run DQ Score</span>
          <span className="text-xl font-bold text-emerald-400">
            {run.dq_score ? `${parseFloat(run.dq_score).toFixed(1)}/100` : '—'}
          </span>
        </div>
      </div>

      {/* 7-Dimension Breakdown */}
      {scores && scores.dimension_scores && (
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2 border-b border-slate-800 pb-2">
            <Award className="w-4 h-4 text-cyan-400" />
            <span>Dimension Score Breakdown for Run #{run.run_id}</span>
          </h2>
          <DimensionBarChart scores={scores.dimension_scores} height={220} />
        </div>
      )}

      {/* Per-Rule Execution Telemetry */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span>Per-Rule Telemetry & Durations ({results.length} Executed Rules)</span>
        </h2>

        <DataTable
          columns={resultColumns}
          data={results}
          keyExtractor={(r) => r.result_id}
          emptyTitle="No Results Logged"
          emptyDescription="No per-rule telemetry results found for this run."
        />
      </div>
    </div>
  );
};
