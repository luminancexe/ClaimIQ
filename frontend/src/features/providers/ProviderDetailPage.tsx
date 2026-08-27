import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Building2, ShieldCheck } from 'lucide-react';
import { getProviderById, getProviderScorecard } from '../../api';

import { ProviderDetail, ProviderScorecard } from '../../types';
import { MetricCard } from '../../components/cards/MetricCard';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/format';

export const ProviderDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [provider, setProvider] = useState<ProviderDetail | null>(null);
  const [scorecard, setScorecard] = useState<ProviderScorecard | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchDetail = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [provData, scoreData] = await Promise.all([
          getProviderById(id),
          getProviderScorecard(id),
        ]);
        setProvider(provData);
        setScorecard(scoreData);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to retrieve provider scorecard';
        const reqId = (err as { requestId?: string })?.requestId;
        setError({ message: msg, requestId: reqId });
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Retrieving Provider Scorecard & Quality History..." />;
  }

  if (error || !provider) {
    return (
      <div className="space-y-4">
        <Link
          to="/providers"
          className="inline-flex items-center space-x-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Providers</span>
        </Link>
        <ErrorAlert
          title="Provider Scorecard Error"
          message={error?.message || 'Provider not found'}
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
            to="/providers"
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold text-slate-100 tracking-tight">
                {provider.first_name} {provider.last_name}
              </h1>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                {provider.provider_reference}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Specialty: <strong className="text-slate-200">{provider.specialty}</strong> &bull; NPI: {provider.npi}
            </p>
          </div>
        </div>
      </div>

      {/* Identity & Practice Context */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-3">
        <h2 className="text-xs font-mono uppercase text-slate-400 border-b border-slate-800 pb-2 flex items-center space-x-1.5">
          <Building2 className="w-4 h-4 text-cyan-400" />
          <span>Clinical & Credentialing Details</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">NPI</span>
            <span className="text-slate-200 font-semibold">{provider.npi}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Taxonomy Code</span>
            <span className="text-slate-200 font-semibold">{provider.taxonomy_code}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Facility Association</span>
            <span className="text-slate-200 font-semibold">
              {scorecard?.facility_name || (provider.facility_id ? `FAC-${provider.facility_id}` : 'Independent')}
            </span>
          </div>
          <div>
            <span className="text-slate-500 block">Provider ID</span>
            <span className="text-cyan-400 font-semibold">#{provider.provider_id}</span>
          </div>
        </div>
      </div>

      {/* Scorecard Metrics Grid */}
      {scorecard && (
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Quality & Operational Scorecard Summary</span>
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
              variant="emerald"
            />
            <MetricCard
              title="Total Paid"
              value={formatCurrency(scorecard.total_paid)}
              variant="emerald"
            />
            <MetricCard
              title="Payment Realization"
              value={formatPercentage(scorecard.payment_rate, true)}
              variant="indigo"
            />
            <MetricCard
              title="Denial Rate"
              value={formatPercentage(scorecard.denial_rate, true)}
              variant="rose"
            />
            <MetricCard
              title="Data Quality Score"
              value={`${scorecard.dq_score.toFixed(1)}/100`}
              variant={scorecard.dq_score >= 90 ? 'emerald' : scorecard.dq_score >= 75 ? 'amber' : 'rose'}
            />
            <MetricCard
              title="Total Issues"
              value={formatNumber(scorecard.issue_count)}
              subValue={`Density: ${scorecard.issue_density.toFixed(2)}`}
              variant="amber"
            />
            <MetricCard
              title="Financial Exposure"
              value={formatCurrency(scorecard.financial_exposure)}
              variant="rose"
            />
          </div>
        </div>
      )}
    </div>
  );
};
