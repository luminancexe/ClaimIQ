import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { FileSpreadsheet, CheckCircle2, XCircle } from 'lucide-react';
import { getClaims } from '../../api';
import { ClaimSummary, ColumnDef } from '../../types';
import { DataTable } from '../../components/tables/DataTable';
import { PaginationBar } from '../../components/tables/PaginationBar';
import { StatusBadge } from '../../components/cards/StatusBadge';
import { SearchInput } from '../../components/filters/SearchInput';
import { SelectFilter } from '../../components/filters/SelectFilter';
import { FilterBar } from '../../components/filters/FilterBar';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatDate } from '../../utils/format';

const STATUS_OPTIONS = [
  { label: 'Submitted', value: 'Submitted' },
  { label: 'Accepted', value: 'Accepted' },
  { label: 'Paid', value: 'Paid' },
  { label: 'Partially Paid', value: 'Partially Paid' },
  { label: 'Denied', value: 'Denied' },
  { label: 'Pending', value: 'Pending' },
  { label: 'Rejected', value: 'Rejected' },
];

export const ClaimsExplorerPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [page, setPage] = useState<number>(() => parseInt(searchParams.get('page') || '1', 10));
  const [pageSize, setPageSize] = useState<number>(() => parseInt(searchParams.get('page_size') || '50', 10));
  const [statusFilter, setStatusFilter] = useState<string>(() => searchParams.get('status') || '');
  const [searchRef, setSearchRef] = useState<string>(() => searchParams.get('claim_reference') || '');

  const [claims, setClaims] = useState<ClaimSummary[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(0);
  const [hasNext, setHasNext] = useState<boolean>(false);
  const [hasPrevious, setHasPrevious] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchClaimsList = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getClaims({
        page,
        page_size: pageSize,
        status: statusFilter || undefined,
        claim_reference: searchRef || undefined,
      });

      setClaims(res?.items || []);
      setTotal(res?.total || 0);
      setTotalPages(res?.total_pages || 0);
      setHasNext(res?.has_next || false);
      setHasPrevious(res?.has_previous || false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch claims data';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, statusFilter, searchRef]);

  useEffect(() => {
    fetchClaimsList();
  }, [fetchClaimsList]);

  const updateUrlParams = (newPage: number, newPageSize: number, newStatus: string, newRef: string) => {
    const params: Record<string, string> = {
      page: String(newPage),
      page_size: String(newPageSize),
    };
    if (newStatus) params.status = newStatus;
    if (newRef) params.claim_reference = newRef;
    setSearchParams(params, { replace: true });
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    updateUrlParams(newPage, pageSize, statusFilter, searchRef);
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setPage(1);
    updateUrlParams(1, newSize, statusFilter, searchRef);
  };

  const handleStatusChange = (newStatus: string) => {
    setStatusFilter(newStatus);
    setPage(1);
    updateUrlParams(1, pageSize, newStatus, searchRef);
  };

  const handleSearchChange = (newRef: string) => {
    setSearchRef(newRef);
    setPage(1);
    updateUrlParams(1, pageSize, statusFilter, newRef);
  };

  const handleResetFilters = () => {
    setStatusFilter('');
    setSearchRef('');
    setPage(1);
    updateUrlParams(1, pageSize, '', '');
  };

  const columns: ColumnDef<ClaimSummary>[] = [
    {
      key: 'claim_reference',
      header: 'Claim Reference',
      cell: (row) => (
        <span className="font-mono text-cyan-400 font-semibold hover:underline">
          {row.claim_reference}
        </span>
      ),
    },
    {
      key: 'patient_id',
      header: 'Patient ID',
      cell: (row) => <span className="font-mono text-slate-400">PT-{String(row.patient_id).padStart(6, '0')}</span>,
    },
    {
      key: 'billing_provider_id',
      header: 'Provider',
      cell: (row) => <span className="font-mono text-slate-300">PRV-{String(row.billing_provider_id).padStart(4, '0')}</span>,
    },
    {
      key: 'payer_id',
      header: 'Payer',
      cell: (row) => <span className="font-mono text-slate-300">PAY-{String(row.payer_id).padStart(3, '0')}</span>,
    },
    {
      key: 'current_status_code',
      header: 'Status',
      cell: (row) => <StatusBadge status={row.current_status_code} />,
    },
    {
      key: 'total_billed_amount',
      header: 'Total Billed',
      align: 'right',
      cell: (row) => (
        <span className="font-mono font-semibold text-slate-100">
          {formatCurrency(row.total_billed_amount)}
        </span>
      ),
    },
    {
      key: 'submission_date',
      header: 'Submitted',
      cell: (row) => <span className="font-mono text-slate-400">{formatDate(row.submission_date)}</span>,
    },
    {
      key: 'is_reconciled',
      header: 'Reconciled',
      align: 'center',
      cell: (row) =>
        row.is_reconciled ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-400 mx-auto" />
        ) : (
          <XCircle className="w-4 h-4 text-slate-500 mx-auto" />
        ),
    },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <FileSpreadsheet className="w-5 h-5 text-cyan-400" />
            <span>Claims Explorer</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Search, filter, and inspect relational healthcare claims across lifecycle states.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <FilterBar onReset={handleResetFilters}>
        <SearchInput
          value={searchRef}
          onChange={handleSearchChange}
          onClear={() => handleSearchChange('')}
          placeholder="Search by Claim Ref (e.g. CLM-)..."
        />

        <SelectFilter
          label="Status"
          value={statusFilter}
          onChange={handleStatusChange}
          options={STATUS_OPTIONS}
          allLabel="All Statuses"
        />
      </FilterBar>

      {error && (
        <ErrorAlert
          title="Claims Loading Error"
          message={error.message}
          requestId={error.requestId}
          onRetry={fetchClaimsList}
        />
      )}

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={claims}
        keyExtractor={(r) => r.claim_id}
        isLoading={isLoading}
        emptyTitle="No Claims Found"
        emptyDescription="No claims matched your search filters. Try clearing or adjusting search parameters."
        onRowClick={(row) => navigate(`/claims/${row.claim_id}`)}
      />

      {/* Pagination Bar */}
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
