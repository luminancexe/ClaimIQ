import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';
import { getRootCauses } from '../../api';
import { RootCauseResponse, RootCauseItem, ColumnDef } from '../../types';
import { ParetoBarChart } from '../../components/charts/ParetoBarChart';
import { DataTable } from '../../components/tables/DataTable';
import { SeverityBadge } from '../../components/cards/SeverityBadge';
import { DimensionBadge } from '../../components/cards/DimensionBadge';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatNumber } from '../../utils/format';

export const RootCausesPage: React.FC = () => {
  const [rootCauses, setRootCauses] = useState<RootCauseResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchRootCauses = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getRootCauses();
      setRootCauses(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve Pareto root causes';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRootCauses();
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Computing Pareto 80/20 Defect Ranking..." />;
  }

  if (error || !rootCauses) {
    return (
      <ErrorAlert
        title="Root Cause Analysis Error"
        message={error?.message || 'Root cause data unavailable'}
        requestId={error?.requestId}
        onRetry={fetchRootCauses}
      />
    );
  }

  const columns: ColumnDef<RootCauseItem>[] = [
    {
      key: 'anomaly_code',
      header: 'Anomaly Code',
      cell: (row) => <span className="font-mono text-cyan-400 font-bold">{row.anomaly_code}</span>,
    },
    {
      key: 'rule_code',
      header: 'Rule Code',
      cell: (row) => <span className="font-mono text-slate-300">{row.rule_code}</span>,
    },
    {
      key: 'description',
      header: 'Anomaly Description',
      cell: (row) => <span className="text-slate-300 text-xs">{row.description}</span>,
    },
    {
      key: 'dimension_code',
      header: 'Dimension',
      cell: (row) => <DimensionBadge dimension={row.dimension_code} />,
    },
    {
      key: 'severity_code',
      header: 'Severity',
      cell: (row) => <SeverityBadge severity={row.severity_code} />,
    },
    {
      key: 'issue_count',
      header: 'Defect Count',
      align: 'right',
      cell: (row) => <span className="font-mono font-bold text-slate-100">{formatNumber(row.issue_count)}</span>,
    },
    {
      key: 'percentage_of_total',
      header: '% of Total',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-300">{row.percentage_of_total.toFixed(1)}%</span>,
    },
    {
      key: 'cumulative_percentage',
      header: 'Cumulative %',
      align: 'right',
      cell: (row) => (
        <span
          className={`font-mono font-bold ${
            row.cumulative_percentage <= 80.0 ? 'text-amber-400' : 'text-slate-400'
          }`}
        >
          {row.cumulative_percentage.toFixed(1)}%
        </span>
      ),
    },
    {
      key: 'financial_exposure',
      header: 'Financial Exposure',
      align: 'right',
      cell: (row) => (
        <span className="font-mono font-semibold text-rose-400">
          {formatCurrency(row.financial_exposure)}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <AlertTriangle className="w-5 h-5 text-cyan-400" />
            <span>Pareto 80/20 Root Cause Analysis</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Isolating the vital-few anomaly mutators generating the majority of data quality errors.
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
        <div className="p-5 bg-surface-card rounded-xl border border-slate-800 space-y-2">
          <span className="text-slate-400 uppercase">Primary Defect Driver</span>
          <div className="text-2xl font-bold text-rose-400">{rootCauses.primary_defect_driver}</div>
          <p className="text-[11px] text-slate-500">Highest individual contributor to QA failures</p>
        </div>

        <div className="p-5 bg-surface-card rounded-xl border border-slate-800 space-y-2">
          <span className="text-slate-400 uppercase">Pareto 80% Cutoff Rank</span>
          <div className="text-2xl font-bold text-amber-400">Top {rootCauses.pareto_cutoff_index} Anomalies</div>
          <p className="text-[11px] text-slate-500">Vital-few codes driving 80% of aggregate issues</p>
        </div>

        <div className="p-5 bg-surface-card rounded-xl border border-slate-800 space-y-2">
          <span className="text-slate-400 uppercase">Total Issues Analyzed</span>
          <div className="text-2xl font-bold text-cyan-400">
            {formatNumber(rootCauses.total_issues_analyzed)}
          </div>
          <p className="text-[11px] text-slate-500">Total defect population across claims dataset</p>
        </div>
      </div>

      {/* Pareto 80/20 Chart */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-100 font-mono flex items-center space-x-2 border-b border-slate-800 pb-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400" />
          <span>Pareto Cumulative Defect Distribution Curve</span>
        </h2>
        <ParetoBarChart items={rootCauses.items} height={320} />
      </div>

      {/* Anomaly Ranking Table */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-100 font-mono">
          Ranked Anomaly Defect Register ({rootCauses.items.length} Anomaly Codes)
        </h2>
        <DataTable
          columns={columns}
          data={rootCauses.items}
          keyExtractor={(item) => item.anomaly_code}
        />
      </div>
    </div>
  );
};
