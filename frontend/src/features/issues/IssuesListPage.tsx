import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { AlertOctagon, ShieldAlert } from 'lucide-react';
import { getIssues } from '../../api';
import { IssueSummary, ColumnDef } from '../../types';
import { DataTable } from '../../components/tables/DataTable';
import { PaginationBar } from '../../components/tables/PaginationBar';
import { SeverityBadge } from '../../components/cards/SeverityBadge';
import { DimensionBadge } from '../../components/cards/DimensionBadge';
import { StatusBadge } from '../../components/cards/StatusBadge';
import { SelectFilter } from '../../components/filters/SelectFilter';
import { FilterBar } from '../../components/filters/FilterBar';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatDateTime } from '../../utils/format';

const SEVERITY_OPTIONS = [
  { label: 'Critical', value: 'Critical' },
  { label: 'High', value: 'High' },
  { label: 'Medium', value: 'Medium' },
  { label: 'Low', value: 'Low' },
];

const DIMENSION_OPTIONS = [
  { label: 'Referential Integrity', value: 'Referential' },
  { label: 'Financial Integrity', value: 'Financial' },
  { label: 'Completeness', value: 'Completeness' },
  { label: 'Validity & Conformance', value: 'Validity' },
  { label: 'Uniqueness', value: 'Uniqueness' },
  { label: 'Temporal Consistency', value: 'Temporal' },
  { label: 'Accuracy & State Logic', value: 'Accuracy' },
];

export const IssuesListPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [page, setPage] = useState<number>(() => parseInt(searchParams.get('page') || '1', 10));
  const [pageSize, setPageSize] = useState<number>(() => parseInt(searchParams.get('page_size') || '50', 10));
  const [severityFilter, setSeverityFilter] = useState<string>(() => searchParams.get('severity') || '');
  const [dimensionFilter, setDimensionFilter] = useState<string>(() => searchParams.get('dimension') || '');

  const [issues, setIssues] = useState<IssueSummary[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [hasNext, setHasNext] = useState<boolean>(false);
  const [hasPrevious, setHasPrevious] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchIssuesList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getIssues({
        page,
        page_size: pageSize,
        severity: severityFilter || undefined,
        dimension: dimensionFilter || undefined,
      });
      setIssues(res?.items || []);
      setTotal(res?.total || 0);
      setTotalPages(res?.total_pages || 0);
      setHasNext(res?.has_next || false);
      setHasPrevious(res?.has_previous || false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch issues list';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, severityFilter, dimensionFilter]);

  useEffect(() => {
    fetchIssuesList();
  }, [fetchIssuesList]);

  const updateUrlParams = (newPage: number, newPageSize: number, newSeverity: string, newDim: string) => {
    const params: Record<string, string> = {
      page: String(newPage),
      page_size: String(newPageSize),
    };
    if (newSeverity) params.severity = newSeverity;
    if (newDim) params.dimension = newDim;
    setSearchParams(params, { replace: true });
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    updateUrlParams(newPage, pageSize, severityFilter, dimensionFilter);
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setPage(1);
    updateUrlParams(1, newSize, severityFilter, dimensionFilter);
  };

  const handleSeverityChange = (newSeverity: string) => {
    setSeverityFilter(newSeverity);
    setPage(1);
    updateUrlParams(1, pageSize, newSeverity, dimensionFilter);
  };

  const handleDimensionChange = (newDim: string) => {
    setDimensionFilter(newDim);
    setPage(1);
    updateUrlParams(1, pageSize, severityFilter, newDim);
  };

  const handleResetFilters = () => {
    setSeverityFilter('');
    setDimensionFilter('');
    setPage(1);
    updateUrlParams(1, pageSize, '', '');
  };

  const columns: ColumnDef<IssueSummary>[] = [
    {
      key: 'issue_reference',
      header: 'Issue Reference',
      cell: (row) => (
        <span className="font-mono text-cyan-400 font-bold hover:underline">
          {row.issue_reference}
        </span>
      ),
    },
    {
      key: 'rule_id',
      header: 'Rule ID',
      cell: (row) => <span className="font-mono text-slate-300">RULE-#{row.rule_id}</span>,
    },
    {
      key: 'claim_id',
      header: 'Claim ID',
      cell: (row) => (
        <span className="font-mono text-slate-400">
          {row.claim_id ? `CLM-#${row.claim_id}` : '—'}
        </span>
      ),
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
      key: 'current_status_code',
      header: 'Status',
      cell: (row) => <StatusBadge status={row.current_status_code} />,
    },
    {
      key: 'variance_amount',
      header: 'Variance',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-rose-400">
          {row.variance_amount ? formatCurrency(row.variance_amount) : '—'}
        </span>
      ),
    },
    {
      key: 'detected_at',
      header: 'Detected Timestamp',
      cell: (row) => (
        <span className="font-mono text-slate-400 text-xs">{formatDateTime(row.detected_at)}</span>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <AlertOctagon className="w-5 h-5 text-cyan-400" />
            <span>Defect Issues Explorer</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Read-only observational telemetry for data quality defects detected across the claims pipeline.
          </p>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1 bg-slate-800/80 rounded-lg border border-slate-700 text-xs font-mono text-slate-400">
          <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
          <span>OBSERVATIONAL VIEW ONLY</span>
        </div>
      </div>

      <FilterBar onReset={handleResetFilters}>
        <SelectFilter
          label="Severity"
          value={severityFilter}
          onChange={handleSeverityChange}
          options={SEVERITY_OPTIONS}
          allLabel="All Severities"
        />

        <SelectFilter
          label="Dimension"
          value={dimensionFilter}
          onChange={handleDimensionChange}
          options={DIMENSION_OPTIONS}
          allLabel="All Dimensions"
        />
      </FilterBar>

      {error && (
        <ErrorAlert
          title="Issues Retrieval Error"
          message={error.message}
          requestId={error.requestId}
          onRetry={fetchIssuesList}
        />
      )}

      <DataTable
        columns={columns}
        data={issues}
        keyExtractor={(i) => i.issue_id}
        isLoading={isLoading}
        emptyTitle="No Issues Found"
        emptyDescription="No defect issues matched your filter criteria."
        onRowClick={(row) => navigate(`/issues/${row.issue_id}`)}
      />

      <PaginationBar
        page={page}
        pageSize={pageSize}
        total={total}
        totalPages={totalPages}
        hasNext={hasNext}
        hasPrevious={hasPrevious}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
      />
    </div>
  );
};
