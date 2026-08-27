import React, { useState, useEffect } from 'react';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { getTrends } from '../../api';
import { DQTrendsSummary, DQTrendPoint, ColumnDef } from '../../types';
import { TrendChart } from '../../components/charts/TrendChart';
import { DataTable } from '../../components/tables/DataTable';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatNumber } from '../../utils/format';

export const TrendsPage: React.FC = () => {
  const [interval, setInterval] = useState<'daily' | 'weekly' | 'monthly'>('monthly');
  const [trends, setTrends] = useState<DQTrendsSummary | null>(null);
  const [showDimensions, setShowDimensions] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchTrends = async (selectedInterval: 'daily' | 'weekly' | 'monthly') => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTrends(selectedInterval);
      setTrends(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve trend time series';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends(interval);
  }, [interval]);

  const columns: ColumnDef<DQTrendPoint>[] = [
    {
      key: 'time_bucket',
      header: 'Time Bucket',
      cell: (row) => <span className="font-mono text-cyan-400 font-bold">{row.time_bucket}</span>,
    },
    {
      key: 'overall_dq_score',
      header: 'DQ Score',
      align: 'right',
      cell: (row) => (
        <span
          className={`font-mono font-bold ${
            row.overall_dq_score >= 90
              ? 'text-emerald-400'
              : row.overall_dq_score >= 75
              ? 'text-amber-400'
              : 'text-rose-400'
          }`}
        >
          {row.overall_dq_score.toFixed(1)}/100
        </span>
      ),
    },
    {
      key: 'claim_volume',
      header: 'Claim Volume',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-300">{formatNumber(row.claim_volume)}</span>,
    },
    {
      key: 'issue_count',
      header: 'Defect Issues',
      align: 'right',
      cell: (row) => (
        <span
          className={`font-mono font-bold ${
            row.issue_count > 0 ? 'text-rose-400' : 'text-emerald-400'
          }`}
        >
          {formatNumber(row.issue_count)}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            <span>Longitudinal Quality Trends</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Time-series analysis of Data Quality scores, issue generation rate, and trajectory velocity.
          </p>
        </div>

        {/* Interval Selector */}
        <div className="flex items-center space-x-2 bg-surface-sidebar p-1 rounded-lg border border-slate-800 font-mono text-xs">
          {(['daily', 'weekly', 'monthly'] as const).map((int) => (
            <button
              key={int}
              onClick={() => setInterval(int)}
              className={`px-3 py-1.5 rounded-md uppercase font-semibold transition ${
                interval === int
                  ? 'bg-cyan-500 text-slate-950 shadow-glow-cyan'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {int}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <ErrorAlert
          title="Trends Telemetry Error"
          message={error.message}
          requestId={error.requestId}
          onRetry={() => fetchTrends(interval)}
        />
      )}

      {isLoading ? (
        <LoadingSpinner size="lg" label="Computing Longitudinal Time Series..." />
      ) : trends ? (
        <>
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-2">
              <span className="text-xs font-mono uppercase text-slate-400">Rolling Average Score</span>
              <div className="text-3xl font-bold font-mono text-cyan-400">
                {trends.rolling_average_score.toFixed(1)}/100
              </div>
              <p className="text-[11px] font-mono text-slate-400">
                Moving average quality score across time windows
              </p>
            </div>

            <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-2">
              <span className="text-xs font-mono uppercase text-slate-400">Score Velocity</span>
              <div className="text-3xl font-bold font-mono text-indigo-400">
                {trends.score_velocity > 0 ? `+${trends.score_velocity.toFixed(2)}` : trends.score_velocity.toFixed(2)}
              </div>
              <p className="text-[11px] font-mono text-slate-400">
                Rate of score change per interval bucket
              </p>
            </div>

            <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-2">
              <span className="text-xs font-mono uppercase text-slate-400">Trend Trajectory</span>
              <div className="flex items-center space-x-2 text-2xl font-bold font-mono">
                {trends.trend_direction === 'IMPROVING' && (
                  <>
                    <ArrowUpRight className="w-6 h-6 text-emerald-400" />
                    <span className="text-emerald-400">IMPROVING</span>
                  </>
                )}
                {trends.trend_direction === 'DEGRADING' && (
                  <>
                    <ArrowDownRight className="w-6 h-6 text-rose-400" />
                    <span className="text-rose-400">DEGRADING</span>
                  </>
                )}
                {trends.trend_direction === 'STABLE' && (
                  <>
                    <Minus className="w-6 h-6 text-slate-400" />
                    <span className="text-slate-300">STABLE</span>
                  </>
                )}
              </div>
              <p className="text-[11px] font-mono text-slate-400">
                Statistical direction evaluated by analytics engine
              </p>
            </div>
          </div>

          {/* Time Series Chart */}
          <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-semibold text-slate-100 font-mono">
                Longitudinal Quality Curve ({interval.toUpperCase()})
              </h2>
              <button
                onClick={() => setShowDimensions(!showDimensions)}
                className="text-xs font-mono text-cyan-400 hover:text-cyan-300 transition"
              >
                {showDimensions ? 'Hide Sub-Dimensions' : 'Show Sub-Dimensions'}
              </button>
            </div>

            <TrendChart
              data={trends.points}
              height={300}
              showDimensions={showDimensions}
            />
          </div>

          {/* Table Breakdown */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-100 font-mono">
              Interval Bucket Matrix
            </h2>
            <DataTable
              columns={columns}
              data={trends.points}
              keyExtractor={(p) => p.time_bucket}
            />
          </div>
        </>
      ) : null}
    </div>
  );
};
