import React, { useState, useEffect } from 'react';
import { Award, AlertTriangle, ShieldCheck } from 'lucide-react';
import { getDQScores } from '../../api';
import { DQScoreSummary, DQDimensionScore, ColumnDef } from '../../types';
import { DataTable } from '../../components/tables/DataTable';
import { DimensionBarChart } from '../../components/charts/DimensionBarChart';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatNumber } from '../../utils/format';

export const DQScoresPage: React.FC = () => {
  const [scores, setScores] = useState<DQScoreSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchScores = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDQScores();
      setScores(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve 7-dimension DQ score telemetry';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchScores();
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Computing 7-Dimension Data Quality Health Scores..." />;
  }

  if (error || !scores) {
    return (
      <ErrorAlert
        title="Scoring Engine Error"
        message={error?.message || 'Unable to compute DQ score matrix'}
        requestId={error?.requestId}
        onRetry={fetchScores}
      />
    );
  }

  const dimensionList = Object.values(scores.dimension_scores || {});
  const overallScore = scores.overall_dq_score;

  const dimensionColumns: ColumnDef<DQDimensionScore>[] = [
    {
      key: 'dimension_name',
      header: 'DQ Dimension',
      cell: (row) => (
        <div>
          <span className="font-semibold text-slate-100">{row.dimension_name}</span>
          <span className="text-[10px] font-mono text-cyan-400 block">{row.dimension_code}</span>
        </div>
      ),
    },
    {
      key: 'weight',
      header: 'Weight',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-300">{(row.weight * 100).toFixed(0)}%</span>,
    },
    {
      key: 'records_evaluated',
      header: 'Records Evaluated',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-300">{formatNumber(row.records_evaluated)}</span>,
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
      key: 'raw_score',
      header: 'Raw Score',
      align: 'right',
      cell: (row) => (
        <span
          className={`font-mono font-bold ${
            row.raw_score >= 90 ? 'text-emerald-400' : row.raw_score >= 75 ? 'text-amber-400' : 'text-rose-400'
          }`}
        >
          {row.raw_score.toFixed(1)}/100
        </span>
      ),
    },
    {
      key: 'weighted_score',
      header: 'Weighted Score',
      align: 'right',
      cell: (row) => (
        <span className="font-mono font-bold text-cyan-400">{row.weighted_score.toFixed(2)} pts</span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <Award className="w-5 h-5 text-cyan-400" />
            <span>7-Dimension Data Quality Scorecard</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Deterministic weighted DQ scoring model evaluating relational integrity and business logic conformance.
          </p>
        </div>
      </div>

      {/* Overall Score & Severity Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Overall Score Display */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-6 flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Composite DQ Score
            </span>
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
          </div>

          <div className="text-center py-2">
            <div
              className={`text-5xl font-black font-mono tracking-tight ${
                overallScore >= 90
                  ? 'text-emerald-400'
                  : overallScore >= 75
                  ? 'text-amber-400'
                  : 'text-rose-400'
              }`}
            >
              {overallScore.toFixed(1)}
              <span className="text-lg font-normal text-slate-500">/100</span>
            </div>
            <span
              className={`inline-block mt-2 px-3 py-0.5 rounded-full text-xs font-mono font-semibold border ${
                overallScore >= 90
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : overallScore >= 75
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}
            >
              {overallScore >= 90
                ? 'OPERATIONAL / OPTIMAL'
                : overallScore >= 75
                ? 'ATTENTION REQUIRED'
                : 'CRITICAL DEFECT RATE'}
            </span>
          </div>

          <div className="flex justify-between text-[11px] font-mono text-slate-400 border-t border-slate-800 pt-3">
            <span>Evaluated: {formatNumber(scores.total_records_evaluated)}</span>
            <span>Total Issues: {formatNumber(scores.total_issues_detected)}</span>
          </div>
        </div>

        {/* Severity Breakdown Card */}
        <div className="md:col-span-2 bg-surface-card border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Issues by Severity Distribution</span>
            </span>
            <span className="text-xs font-mono text-cyan-400">
              {formatNumber(scores.total_issues_detected)} Total Issues
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-center font-mono">
              <span className="text-[10px] text-rose-400 uppercase block font-semibold">Critical</span>
              <span className="text-xl font-bold text-rose-300">
                {formatNumber(scores.severity_breakdown?.Critical || 0)}
              </span>
            </div>
            <div className="p-3 bg-rose-500/5 border border-rose-500/20 rounded-lg text-center font-mono">
              <span className="text-[10px] text-rose-400 uppercase block">High</span>
              <span className="text-xl font-bold text-rose-400">
                {formatNumber(scores.severity_breakdown?.High || 0)}
              </span>
            </div>
            <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-center font-mono">
              <span className="text-[10px] text-amber-400 uppercase block">Medium</span>
              <span className="text-xl font-bold text-amber-300">
                {formatNumber(scores.severity_breakdown?.Medium || 0)}
              </span>
            </div>
            <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-center font-mono">
              <span className="text-[10px] text-cyan-400 uppercase block">Low</span>
              <span className="text-xl font-bold text-cyan-300">
                {formatNumber(scores.severity_breakdown?.Low || 0)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Visual Dimension Bar Chart */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-100 font-mono">
          Dimension Performance Comparison
        </h2>
        <DimensionBarChart scores={scores.dimension_scores || {}} height={240} />
      </div>

      {/* 7-Dimension Detailed Table */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-100 font-mono">
          Dimension Weighted Calculation Matrix
        </h2>
        <DataTable
          columns={dimensionColumns}
          data={dimensionList}
          keyExtractor={(d) => d.dimension_code}
        />
      </div>
    </div>
  );
};
