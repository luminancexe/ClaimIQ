import React, { useState, useEffect } from 'react';
import { Activity, DollarSign, AlertOctagon, CheckCircle2, ShieldAlert } from 'lucide-react';
import { getKPIAnalytics } from '../../api';
import { KPIOverview } from '../../types';
import { MetricCard } from '../../components/cards/MetricCard';
import { StatusDonut } from '../../components/charts/StatusDonut';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/format';

export const KPIsPage: React.FC = () => {
  const [kpis, setKpis] = useState<KPIOverview | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchKpis = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getKPIAnalytics();
      setKpis(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve operational KPIs';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchKpis();
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Aggregating Operational KPI Telemetry..." />;
  }

  if (error || !kpis) {
    return (
      <ErrorAlert
        title="KPI Telemetry Error"
        message={error?.message || 'KPI metrics unavailable'}
        requestId={error?.requestId}
        onRetry={fetchKpis}
      />
    );
  }

  const { claims, payments, denials, qa } = kpis;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span>Operational Key Performance Indicators</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Executive operational benchmarks across claims velocity, payments, denial prevention, and QA density.
          </p>
        </div>
      </div>

      {/* Section 1: Claims & Payment Volume KPIs */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span>Claims & Adjudication Volume</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total Claims Volume"
            value={formatNumber(claims.total_claims)}
            variant="cyan"
          />
          <MetricCard
            title="Adjudication Rate"
            value={formatPercentage(claims.adjudication_rate, true)}
            subValue={`${formatNumber(claims.adjudicated_claims)} Adjudicated`}
            variant="emerald"
          />
          <MetricCard
            title="Reconciled Claims"
            value={formatNumber(claims.reconciled_claims)}
            subValue={`${formatPercentage(claims.reconciled_claims / (claims.total_claims || 1), true)} of Total`}
            variant="indigo"
          />
          <MetricCard
            title="Total Payments Issued"
            value={formatNumber(payments.total_payments_count)}
            subValue={`Zero-Pay: ${payments.zero_payment_count}`}
            variant="amber"
          />
        </div>
      </div>

      {/* Section 2: Financial Payment KPIs */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2">
          <DollarSign className="w-4 h-4 text-emerald-400" />
          <span>Payment Velocity & Averages</span>
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <MetricCard
            title="Total Paid Amount"
            value={formatCurrency(payments.total_paid_amount)}
            variant="emerald"
          />
          <MetricCard
            title="Average Payment per Claim"
            value={formatCurrency(payments.average_payment_amount)}
            variant="cyan"
          />
          <MetricCard
            title="Payment Turnaround Velocity"
            value={
              payments.average_payment_turnaround_days !== null &&
              payments.average_payment_turnaround_days !== undefined
                ? `${payments.average_payment_turnaround_days.toFixed(1)} Days`
                : '—'
            }
            variant="indigo"
          />
        </div>
      </div>

      {/* Section 3: Denials & QA Density */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Denial KPIs */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2 border-b border-slate-800 pb-2">
            <AlertOctagon className="w-4 h-4 text-rose-400" />
            <span>Denial Telemetry & Financial Impact</span>
          </h3>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Total Denials</span>
              <span className="text-xl font-bold text-rose-400">{formatNumber(denials.total_denials)}</span>
            </div>
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Denial Rate</span>
              <span className="text-xl font-bold text-rose-400">{formatPercentage(denials.denial_rate, true)}</span>
            </div>
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Appealable Rate</span>
              <span className="text-xl font-bold text-amber-400">{formatPercentage(denials.appealable_rate, true)}</span>
            </div>
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Financial Exposure</span>
              <span className="text-xl font-bold text-rose-400">{formatCurrency(denials.denial_financial_exposure)}</span>
            </div>
          </div>
        </div>

        {/* QA Density KPIs */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2 border-b border-slate-800 pb-2">
            <ShieldAlert className="w-4 h-4 text-cyan-400" />
            <span>Data Quality Health & Defect Density</span>
          </h3>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Average DQ Score</span>
              <span className="text-xl font-bold text-emerald-400">{qa.average_dq_score.toFixed(1)}/100</span>
            </div>
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Clean Record Rate</span>
              <span className="text-xl font-bold text-emerald-400">{formatPercentage(qa.clean_record_rate, true)}</span>
            </div>
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Defect Density</span>
              <span className="text-xl font-bold text-cyan-400">{qa.defect_density.toFixed(2)} issues/rec</span>
            </div>
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-400 block mb-1">Total Issues</span>
              <span className="text-xl font-bold text-rose-400">{formatNumber(qa.total_issues)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Claim Status Lifecycle Donut */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2 border-b border-slate-800 pb-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>Status Lifecycle Breakdown</span>
        </h2>
        <StatusDonut distribution={claims.status_distribution} height={240} />
      </div>
    </div>
  );
};
