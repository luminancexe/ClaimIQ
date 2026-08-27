import React, { useState, useEffect } from 'react';
import { DollarSign, ShieldCheck, TrendingUp, AlertTriangle } from 'lucide-react';
import { getFinancialAnalytics } from '../../api';
import { FinancialOverview } from '../../types';
import { MetricCard } from '../../components/cards/MetricCard';
import { FinancialBreakdownChart } from '../../components/charts/FinancialBreakdownChart';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatPercentage } from '../../utils/format';

export const FinancialPage: React.FC = () => {
  const [financial, setFinancial] = useState<FinancialOverview | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchFinancial = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getFinancialAnalytics();
      setFinancial(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch financial analytics';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFinancial();
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Computing Financial Integrity & Reconciliation Metrics..." />;
  }

  if (error || !financial) {
    return (
      <ErrorAlert
        title="Financial Telemetry Error"
        message={error?.message || 'Financial analytics unavailable'}
        requestId={error?.requestId}
        onRetry={fetchFinancial}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <DollarSign className="w-5 h-5 text-cyan-400" />
            <span>Financial Integrity & Reconciliation</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Relational adjudication rollups, variance isolation, and over/underpayment exposure metrics.
          </p>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Billed"
          value={formatCurrency(financial.total_billed)}
          icon={<DollarSign className="w-4 h-4" />}
          variant="cyan"
        />

        <MetricCard
          title="Total Paid"
          value={formatCurrency(financial.total_paid)}
          icon={<DollarSign className="w-4 h-4" />}
          variant="emerald"
        />

        <MetricCard
          title="Contractual Adjustments"
          value={formatCurrency(financial.total_contractual_adjustments)}
          icon={<TrendingUp className="w-4 h-4" />}
          variant="indigo"
        />

        <MetricCard
          title="Patient Responsibility"
          value={formatCurrency(financial.total_patient_responsibility)}
          icon={<DollarSign className="w-4 h-4" />}
          variant="amber"
        />

        <MetricCard
          title="Total Variance"
          value={formatCurrency(financial.total_variance)}
          icon={<AlertTriangle className="w-4 h-4" />}
          variant="rose"
        />

        <MetricCard
          title="Overpayment Exposure"
          value={formatCurrency(financial.overpayment_exposure)}
          icon={<AlertTriangle className="w-4 h-4" />}
          variant="rose"
        />

        <MetricCard
          title="Underpayment Exposure"
          value={formatCurrency(financial.underpayment_exposure)}
          icon={<AlertTriangle className="w-4 h-4" />}
          variant="amber"
        />

        <MetricCard
          title="Total Denied"
          value={formatCurrency(financial.total_denied_amount)}
          icon={<AlertTriangle className="w-4 h-4" />}
          variant="rose"
        />
      </div>

      {/* Ratios & Integrity Rates */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 text-center space-y-2">
          <span className="text-xs font-mono uppercase text-slate-400">Reconciliation Rate</span>
          <div className="text-3xl font-bold font-mono text-emerald-400">
            {formatPercentage(financial.reconciliation_rate, true)}
          </div>
          <p className="text-[11px] text-slate-400 font-mono">
            Proportion of adjudicated claims with balanced ledger entries
          </p>
        </div>

        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 text-center space-y-2">
          <span className="text-xs font-mono uppercase text-slate-400">Payment Realization Rate</span>
          <div className="text-3xl font-bold font-mono text-cyan-400">
            {formatPercentage(financial.payment_rate, true)}
          </div>
          <p className="text-[11px] text-slate-400 font-mono">
            Ratio of paid dollars to total billed claims volume
          </p>
        </div>

        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 text-center space-y-2">
          <span className="text-xs font-mono uppercase text-slate-400">Financial Integrity Rate</span>
          <div className="text-3xl font-bold font-mono text-indigo-400">
            {formatPercentage(financial.financial_integrity_rate, true)}
          </div>
          <p className="text-[11px] text-slate-400 font-mono">
            Overall financial consistency and zero-variance compliance
          </p>
        </div>
      </div>

      {/* Financial Breakdown Chart */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2 border-b border-slate-800 pb-3">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span>Financial Reconciliation Distribution</span>
        </h2>
        <FinancialBreakdownChart financial={financial} height={280} />
      </div>
    </div>
  );
};
