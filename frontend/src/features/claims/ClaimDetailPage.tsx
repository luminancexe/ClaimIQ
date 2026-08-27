import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileSpreadsheet,
  ArrowLeft,
  DollarSign,
  Calendar,
  User,
  Building2,
  Clock,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { getClaimById, getClaimLines, getClaimHistory } from '../../api';
import { ClaimDetail, ClaimLine, StatusHistoryEntry } from '../../types';
import { StatusBadge } from '../../components/cards/StatusBadge';
import { DataTable, ColumnDef } from '../../components/tables/DataTable';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatDate, formatDateTime } from '../../utils/format';

export const ClaimDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [claim, setClaim] = useState<ClaimDetail | null>(null);
  const [lines, setLines] = useState<ClaimLine[]>([]);
  const [history, setHistory] = useState<StatusHistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchDetail = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [claimData, linesData, historyData] = await Promise.all([
          getClaimById(id),
          getClaimLines(id),
          getClaimHistory(id),
        ]);
        setClaim(claimData);
        setLines(linesData);
        setHistory(historyData);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to fetch claim detail';
        const reqId = (err as { requestId?: string })?.requestId;
        setError({ message: msg, requestId: reqId });
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetail();
  }, [id]);

  if (isLoading) {
    return (
      <div className="py-20">
        <LoadingSpinner size="lg" label="Retrieving Claim Artifacts & Adjudication Rollups..." />
      </div>
    );
  }

  if (error || !claim) {
    return (
      <div className="space-y-4">
        <Link
          to="/claims"
          className="inline-flex items-center space-x-1.5 text-xs font-mono text-cyan-400 hover:text-cyan-300 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Claims</span>
        </Link>
        <ErrorAlert
          title="Claim Retrieval Error"
          message={error?.message || 'Claim not found'}
          requestId={error?.requestId}
        />
      </div>
    );
  }

  const lineColumns: ColumnDef<ClaimLine>[] = [
    {
      key: 'line_number',
      header: 'Line #',
      cell: (row) => <span className="font-mono text-slate-400">{row.line_number}</span>,
    },
    {
      key: 'cpt_code',
      header: 'CPT Code',
      cell: (row) => <span className="font-mono text-cyan-400 font-semibold">{row.cpt_code}</span>,
    },
    {
      key: 'procedure_description',
      header: 'Description',
      cell: (row) => (
        <span className="text-slate-300 max-w-xs truncate block">
          {row.procedure_description || 'Standard Medical Service'}
        </span>
      ),
    },
    {
      key: 'units',
      header: 'Units',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-300">{row.units}</span>,
    },
    {
      key: 'unit_price',
      header: 'Unit Price',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-300">{formatCurrency(row.unit_price)}</span>,
    },
    {
      key: 'line_billed_amount',
      header: 'Billed Amount',
      align: 'right',
      cell: (row) => (
        <span className="font-mono font-semibold text-slate-100">
          {formatCurrency(row.line_billed_amount)}
        </span>
      ),
    },
    {
      key: 'line_status',
      header: 'Line Status',
      cell: (row) => <StatusBadge status={row.line_status} />,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <Link
            to="/claims"
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold font-mono text-cyan-400 tracking-tight">
                {claim.claim_reference}
              </h1>
              <StatusBadge status={claim.current_status_code} />
              {claim.is_reconciled ? (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Reconciled</span>
                </span>
              ) : (
                <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                  <XCircle className="w-3.5 h-3.5" />
                  <span>Unreconciled</span>
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">
              Claim ID: #{claim.claim_id} &bull; Encounter ID: #{claim.encounter_id}
            </p>
          </div>
        </div>
      </div>

      {/* Metadata & Financial Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Claim Metadata */}
        <div className="lg:col-span-2 bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-xs font-mono uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2">
            Claim Identity & Clinical Context
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs font-mono">
            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-500 flex items-center space-x-1 mb-1">
                <User className="w-3.5 h-3.5" />
                <span>Patient ID</span>
              </span>
              <span className="text-slate-200 font-semibold">
                PT-{String(claim.patient_id).padStart(6, '0')}
              </span>
            </div>

            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-500 flex items-center space-x-1 mb-1">
                <User className="w-3.5 h-3.5" />
                <span>Billing Provider</span>
              </span>
              <span className="text-slate-200 font-semibold">
                PRV-{String(claim.billing_provider_id).padStart(4, '0')}
              </span>
            </div>

            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-500 flex items-center space-x-1 mb-1">
                <Building2 className="w-3.5 h-3.5" />
                <span>Payer ID</span>
              </span>
              <span className="text-slate-200 font-semibold">
                PAY-{String(claim.payer_id).padStart(3, '0')}
              </span>
            </div>

            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-500 flex items-center space-x-1 mb-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>Submission Date</span>
              </span>
              <span className="text-slate-200 font-semibold">{formatDate(claim.submission_date)}</span>
            </div>

            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-500 flex items-center space-x-1 mb-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>Adjudication Date</span>
              </span>
              <span className="text-slate-200 font-semibold">
                {claim.adjudication_date ? formatDate(claim.adjudication_date) : 'Pending Adjudication'}
              </span>
            </div>

            <div className="p-3 bg-surface-sidebar rounded-lg border border-slate-800">
              <span className="text-slate-500 flex items-center space-x-1 mb-1">
                <FileSpreadsheet className="w-3.5 h-3.5" />
                <span>Service Lines</span>
              </span>
              <span className="text-cyan-400 font-semibold">{lines.length} Lines</span>
            </div>
          </div>
        </div>

        {/* Right 1 Col: Financial Rollup */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-xs font-mono uppercase tracking-wider text-slate-400 border-b border-slate-800 pb-2 flex items-center justify-between">
            <span>Financial Rollup</span>
            <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
          </h2>

          <div className="space-y-3 text-xs font-mono">
            <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Total Billed:</span>
              <span className="text-slate-100 font-bold text-sm">
                {formatCurrency(claim.total_billed_amount)}
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Total Paid:</span>
              <span className="text-emerald-400 font-bold">
                {formatCurrency(claim.total_paid || '0.00')}
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Adjustments:</span>
              <span className="text-indigo-400 font-semibold">
                {formatCurrency(claim.total_adjusted || '0.00')}
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Denied Exposure:</span>
              <span className="text-rose-400 font-semibold">
                {formatCurrency(claim.total_denied || '0.00')}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Itemized Claim Lines */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-100 font-mono tracking-wide flex items-center space-x-2">
          <FileSpreadsheet className="w-4 h-4 text-cyan-400" />
          <span>Itemized Claim Lines ({lines.length})</span>
        </h2>

        <DataTable
          columns={lineColumns}
          data={lines}
          keyExtractor={(l) => l.claim_line_id}
          emptyTitle="No Line Items"
          emptyDescription="This claim has no itemized procedure lines."
        />
      </div>

      {/* Lifecycle Status History Timeline */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-100 font-mono tracking-wide flex items-center space-x-2 border-b border-slate-800 pb-3">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span>Lifecycle Status Transition History</span>
        </h2>

        {history.length === 0 ? (
          <p className="text-xs text-slate-500 font-mono">No status transition events logged.</p>
        ) : (
          <div className="space-y-3">
            {history.map((item, idx) => (
              <div
                key={item.history_id}
                className="flex items-start space-x-3 text-xs font-mono py-2 border-b border-slate-800/60 last:border-0"
              >
                <div className="w-6 h-6 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 text-[10px] font-bold shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center space-x-2">
                    {item.previous_status_code && (
                      <>
                        <StatusBadge status={item.previous_status_code} />
                        <span className="text-slate-500">&rarr;</span>
                      </>
                    )}
                    <StatusBadge status={item.new_status_code} />
                    <span className="text-slate-500 font-sans">&bull;</span>
                    <span className="text-slate-400">{formatDateTime(item.transition_timestamp)}</span>
                  </div>
                  {item.transition_reason && (
                    <p className="text-slate-300 text-[11px]">{item.transition_reason}</p>
                  )}
                  <p className="text-[10px] text-slate-500">
                    Actor: <span className="text-slate-400">{item.actor_reference}</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
