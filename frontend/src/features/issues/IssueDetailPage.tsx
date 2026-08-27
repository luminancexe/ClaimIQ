import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ShieldAlert, FileSpreadsheet } from 'lucide-react';
import { getIssueById } from '../../api';

import { IssueDetail } from '../../types';
import { SeverityBadge } from '../../components/cards/SeverityBadge';
import { DimensionBadge } from '../../components/cards/DimensionBadge';
import { StatusBadge } from '../../components/cards/StatusBadge';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatDateTime } from '../../utils/format';

export const IssueDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchDetail = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getIssueById(id);
        setIssue(data);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to retrieve issue detail';
        const reqId = (err as { requestId?: string })?.requestId;
        setError({ message: msg, requestId: reqId });
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Retrieving Defect Telemetry Record..." />;
  }

  if (error || !issue) {
    return (
      <div className="space-y-4">
        <Link
          to="/issues"
          className="inline-flex items-center space-x-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Issues</span>
        </Link>
        <ErrorAlert
          title="Issue Retrieval Error"
          message={error?.message || 'Issue not found'}
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
            to="/issues"
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold font-mono text-cyan-400 tracking-tight">
                {issue.issue_reference}
              </h1>
              <SeverityBadge severity={issue.severity_code} />
              <DimensionBadge dimension={issue.dimension_code} />
              <StatusBadge status={issue.current_status_code} />
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Issue ID: #{issue.issue_id} &bull; Detected: {formatDateTime(issue.detected_at)}
            </p>
          </div>
        </div>
      </div>

      {/* Read-Only Observational Callout */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-center space-x-3 text-xs font-mono text-slate-400">
        <ShieldAlert className="w-5 h-5 text-cyan-400 shrink-0" />
        <div>
          <span className="font-semibold text-slate-200 block">Observational Telemetry Mode</span>
          <span>
            ClaimIQ Phase 8 provides read-only observation. Issue triage, assignment workflows, and remediation transitions belong to Phase 9.
          </span>
        </div>
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Rule Context */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-3 font-mono text-xs">
          <h2 className="text-xs uppercase text-slate-400 border-b border-slate-800 pb-2 font-semibold">
            Validation Rule Context
          </h2>
          <div className="space-y-2">
            <div>
              <span className="text-slate-500 block">Rule Code</span>
              <span className="text-cyan-400 font-bold">{issue.rule_code || `RULE-#${issue.rule_id}`}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Rule Name</span>
              <span className="text-slate-200 font-semibold">{issue.rule_name || 'Standard QA Validation'}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Rule ID</span>
              <span className="text-slate-300">#{issue.rule_id}</span>
            </div>
          </div>
        </div>

        {/* Claim & Financial Context */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-3 font-mono text-xs">
          <h2 className="text-xs uppercase text-slate-400 border-b border-slate-800 pb-2 font-semibold">
            Entity & Financial Impact
          </h2>
          <div className="space-y-2">
            <div>
              <span className="text-slate-500 block">Associated Claim ID</span>
              {issue.claim_id ? (
                <Link
                  to={`/claims/${issue.claim_id}`}
                  className="text-cyan-400 font-semibold hover:underline inline-flex items-center space-x-1"
                >
                  <FileSpreadsheet className="w-3.5 h-3.5" />
                  <span>Claim #{issue.claim_id}</span>
                </Link>
              ) : (
                <span className="text-slate-500">Unassociated / Batch Defect</span>
              )}
            </div>
            <div>
              <span className="text-slate-500 block">Financial Variance Exposure</span>
              <span className="text-rose-400 font-bold text-sm">
                {issue.variance_amount ? formatCurrency(issue.variance_amount) : '$0.00'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block">Root Cause Code</span>
              <span className="text-amber-400 font-semibold">{issue.root_cause_code || 'UNASSIGNED'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
