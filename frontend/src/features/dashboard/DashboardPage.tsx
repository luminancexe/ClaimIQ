import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldAlert,
  DollarSign,
  FileSpreadsheet,
  AlertOctagon,
  TrendingUp,
  Activity,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';
import { getAnalyticsOverview, getTrends, getDQScores } from '../../api';
import {
  AnalyticsOverview,
  DQTrendsSummary,
  DQScoreSummary,
} from '../../types';
import { MetricCard } from '../../components/cards/MetricCard';
import { TrendChart } from '../../components/charts/TrendChart';
import { StatusDonut } from '../../components/charts/StatusDonut';
import { DimensionBarChart } from '../../components/charts/DimensionBarChart';
import { ParetoBarChart } from '../../components/charts/ParetoBarChart';
import { FinancialBreakdownChart } from '../../components/charts/FinancialBreakdownChart';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import {
  formatCurrency,
  formatPercentage,
  formatNumber,
} from '../../utils/format';

export const DashboardPage: React.FC = () => {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [trends, setTrends] = useState<DQTrendsSummary | null>(null);
  const [scores, setScores] = useState<DQScoreSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [overviewData, trendsData, scoresData] = await Promise.all([
        getAnalyticsOverview(),
        getTrends('monthly'),
        getDQScores(),
      ]);
      setOverview(overviewData);
      setTrends(trendsData);
      setScores(scoresData);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load operational dashboard data';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="py-20">
        <LoadingSpinner size="lg" label="Aggregating Healthcare Telemetry & QA Signals..." />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorAlert
        title="Dashboard Telemetry Error"
        message={error.message}
        requestId={error.requestId}
        onRetry={fetchDashboardData}
      />
    );
  }

  const financial = overview?.financial;
  const kpis = overview?.kpis;
  const rootCauses = overview?.root_cause;

  const dqScore = scores?.overall_dq_score ?? kpis?.qa.average_dq_score ?? 100.0;
  const dqTrendDirection = trends?.trend_direction || 'STABLE';

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span>Operations & Data Quality Console</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Deterministic synthetic claims dataset monitoring &bull; Real-time QA scoring &bull; Financial integrity
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/qa/scores"
            className="px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-mono transition flex items-center space-x-1.5"
          >
            <span>View 7-Dimension Scores</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Top 8 KPI Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Claims"
          value={formatNumber(kpis?.claims.total_claims || 0)}
          subValue={`${formatPercentage(kpis?.claims.adjudication_rate || 0, true)} Adj.`}
          icon={<FileSpreadsheet className="w-4 h-4" />}
          variant="cyan"
        />

        <MetricCard
          title="Total Billed"
          value={formatCurrency(financial?.total_billed)}
          subValue={`Paid: ${formatCurrency(financial?.total_paid)}`}
          icon={<DollarSign className="w-4 h-4" />}
          variant="emerald"
        />

        <MetricCard
          title="Denial Rate"
          value={formatPercentage(kpis?.denials.denial_rate || 0, true)}
          subValue={`${formatPercentage(kpis?.denials.appealable_rate || 0, true)} Appealable`}
          icon={<AlertOctagon className="w-4 h-4" />}
          variant="rose"
        />

        <MetricCard
          title="Overall DQ Score"
          value={`${dqScore.toFixed(1)}/100`}
          trend={dqTrendDirection === 'IMPROVING' ? 'up' : dqTrendDirection === 'DEGRADING' ? 'down' : 'neutral'}
          trendText={`Trajectory: ${dqTrendDirection}`}
          icon={<ShieldAlert className="w-4 h-4" />}
          variant={dqScore >= 90 ? 'emerald' : dqScore >= 75 ? 'amber' : 'rose'}
        />

        <MetricCard
          title="Total QA Issues"
          value={formatNumber(kpis?.qa.total_issues || 0)}
          subValue={`${kpis?.qa.issues_by_severity?.Critical || 0} Critical`}
          icon={<AlertOctagon className="w-4 h-4" />}
          variant="rose"
        />

        <MetricCard
          title="Financial Exposure"
          value={formatCurrency(financial?.overpayment_exposure || financial?.total_variance)}
          subValue={`Var: ${formatCurrency(financial?.total_variance)}`}
          icon={<DollarSign className="w-4 h-4" />}
          variant="amber"
        />

        <MetricCard
          title="Clean Record Rate"
          value={formatPercentage(kpis?.qa.clean_record_rate || 0, true)}
          subValue={`Density: ${kpis?.qa.defect_density?.toFixed(2) || '0.00'}`}
          icon={<CheckCircle2 className="w-4 h-4" />}
          variant="emerald"
        />

        <MetricCard
          title="Reconciliation Rate"
          value={formatPercentage(financial?.reconciliation_rate || 0, true)}
          subValue={`Integrity: ${formatPercentage(financial?.financial_integrity_rate || 0, true)}`}
          icon={<TrendingUp className="w-4 h-4" />}
          variant="indigo"
        />
      </div>

      {/* Row 2: DQ Scores Breakdown & Claims Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 7-Dimension DQ Breakdown */}
        <div className="lg:col-span-2 bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 font-mono tracking-wide">
                7-Dimension Data Quality Health
              </h2>
              <p className="text-xs text-slate-400">
                Weighted scoring model evaluating referential, financial, temporal, and logic rules.
              </p>
            </div>
            <Link to="/qa/scores" className="text-xs font-mono text-cyan-400 hover:text-cyan-300">
              Details &rarr;
            </Link>
          </div>

          <DimensionBarChart scores={scores?.dimension_scores || {}} height={220} />
        </div>

        {/* Claim Status Distribution */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 font-mono tracking-wide">
                Claims Lifecycle Status
              </h2>
              <p className="text-xs text-slate-400">Distribution across operational states.</p>
            </div>
            <Link to="/claims" className="text-xs font-mono text-cyan-400 hover:text-cyan-300">
              Explore &rarr;
            </Link>
          </div>

          <StatusDonut distribution={kpis?.claims.status_distribution || {}} height={220} />
        </div>
      </div>

      {/* Row 3: Longitudinal Trends & Financial Integrity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Longitudinal Trends */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 font-mono tracking-wide">
                Longitudinal Quality Trend
              </h2>
              <p className="text-xs text-slate-400">Time-series DQ trajectory & velocity metrics.</p>
            </div>
            <Link to="/analytics/trends" className="text-xs font-mono text-cyan-400 hover:text-cyan-300">
              Trends Hub &rarr;
            </Link>
          </div>

          <TrendChart data={trends?.points || []} height={240} />
        </div>

        {/* Financial Breakdown */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 font-mono tracking-wide">
                Financial Integrity Breakdown
              </h2>
              <p className="text-xs text-slate-400">Billed vs. Paid, Adjustments, and Unreconciled Variance.</p>
            </div>
            <Link to="/analytics/financial" className="text-xs font-mono text-cyan-400 hover:text-cyan-300">
              Reconciliation &rarr;
            </Link>
          </div>

          {financial ? (
            <FinancialBreakdownChart financial={financial} height={240} />
          ) : (
            <div className="h-60 flex items-center justify-center text-xs text-slate-500 font-mono">
              No financial telemetry available
            </div>
          )}
        </div>
      </div>

      {/* Row 4: Top Pareto Defect Drivers */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-100 font-mono tracking-wide">
              Top Pareto Root Cause Defect Drivers
            </h2>
            <p className="text-xs text-slate-400">
              Vital few anomaly codes driving ~80% of data quality issues across the synthetic claims pipeline.
            </p>
          </div>
          <Link to="/analytics/root-causes" className="text-xs font-mono text-cyan-400 hover:text-cyan-300">
            Full Pareto Analysis &rarr;
          </Link>
        </div>

        <ParetoBarChart items={rootCauses?.items || []} height={260} />
      </div>
    </div>
  );
};
