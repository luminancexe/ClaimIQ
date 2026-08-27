import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Building2, ArrowLeft, ShieldCheck } from 'lucide-react';
import { getPayerById, getPayerScorecard } from '../../api';

import { PayerDetail, PayerScorecard } from '../../types';
import { MetricCard } from '../../components/cards/MetricCard';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/format';

export const PayerDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [payer, setPayer] = useState<PayerDetail | null>(null);
  const [scorecard, setScorecard] = useState<PayerScorecard | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchDetail = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [payerData, scoreData] = await Promise.all([
          getPayerById(id),
          getPayerScorecard(id),
        ]);
        setPayer(payerData);
        setScorecard(scoreData);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to retrieve payer scorecard';
        const reqId = (err as { requestId?: string })?.requestId;
        setError({ message: msg, requestId: reqId });
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Retrieving Payer Scorecard & Adjudication Turnarounds..." />;
  }

  if (error || !payer) {
    return (
      <div className="space-y-4">
        <Link
          to="/payers"
          className="inline-flex items-center space-x-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Payers</span>
        </Link>
        <ErrorAlert
          title="Payer Scorecard Error"
          message={error?.message || 'Payer not found'}
          requestId={error?.requestId}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <Link
            to="/payers"
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold text-slate-100 tracking-tight">{payer.payer_name}</h1>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                {payer.payer_reference}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Type: <strong className="text-slate-200">{payer.payer_type}</strong> &bull; Timely Filing Limit: {payer.timely_filing_days} Days
            </p>
          </div>
        </div>
      </div>

      {/* Identity Context */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-3">
        <h2 className="text-xs font-mono uppercase text-slate-400 border-b border-slate-800 pb-2 flex items-center space-x-1.5">
          <Building2 className="w-4 h-4 text-cyan-400" />
          <span>Payer Policy & Filing Terms</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">Payer ID</span>
            <span className="text-cyan-400 font-semibold">#{payer.payer_id}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Payer Type</span>
            <span className="text-slate-200 font-semibold">{payer.payer_type}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Timely Filing Window</span>
            <span className="text-slate-200 font-semibold">{payer.timely_filing_days} Days</span>
          </div>
          <div>
            <span className="text-slate-500 block">Filing Compliance</span>
            <span className="text-emerald-400 font-semibold">
              {scorecard ? formatPercentage(scorecard.timely_filing_compliance_rate, true) : '—'}
            </span>
          </div>
        </div>
      </div>

      {/* Scorecard Metrics Grid */}
      {scorecard && (
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Adjudication Performance Scorecard</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Claim Volume"
              value={formatNumber(scorecard.claim_volume)}
              variant="cyan"
            />
            <MetricCard
              title="Total Billed"
              value={formatCurrency(scorecard.total_billed)}
              variant="cyan"
            />
            <MetricCard
              title="Total Paid"
              value={formatCurrency(scorecard.total_paid)}
              variant="emerald"
            />
            <MetricCard
              title="Payment Realization Rate"
              value={formatPercentage(scorecard.payment_rate, true)}
              variant="indigo"
            />
            <MetricCard
              title="Denial Rate"
              value={formatPercentage(scorecard.denial_rate, true)}
              variant="rose"
            />
            <MetricCard
              title="Avg Adjudication Latency"
              value={`${scorecard.average_adjudication_latency_days.toFixed(1)} Days`}
              variant="indigo"
            />
            <MetricCard
              title="Avg Payment Latency"
              value={`${scorecard.average_payment_latency_days.toFixed(1)} Days`}
              variant="indigo"
            />
            <MetricCard
              title="Contractual Adj Ratio"
              value={formatPercentage(scorecard.contractual_adjustment_ratio, true)}
              variant="amber"
            />
          </div>
        </div>
      )}
    </div>
  );
};
