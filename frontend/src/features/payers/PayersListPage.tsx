import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2 } from 'lucide-react';
import { getPayerAnalytics } from '../../api';
import { PayerScorecard, ColumnDef } from '../../types';
import { DataTable } from '../../components/tables/DataTable';
import { SearchInput } from '../../components/filters/SearchInput';
import { SelectFilter } from '../../components/filters/SelectFilter';
import { FilterBar } from '../../components/filters/FilterBar';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/format';


export const PayersListPage: React.FC = () => {
  const navigate = useNavigate();
  const [scorecards, setScorecards] = useState<PayerScorecard[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchScorecards = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getPayerAnalytics();
      setScorecards(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve payer scorecards';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchScorecards();
  }, []);

  const payerTypes = useMemo(() => {
    const set = new Set<string>();
    scorecards.forEach((s) => {
      if (s.payer_type) set.add(s.payer_type);
    });
    return Array.from(set).map((t) => ({ label: t, value: t }));
  }, [scorecards]);

  const filteredScorecards = useMemo(() => {
    return scorecards.filter((s) => {
      const matchesSearch =
        !searchQuery.trim() ||
        s.payer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.payer_reference.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.payer_type.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesType = !typeFilter || s.payer_type === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [scorecards, searchQuery, typeFilter]);

  const columns: ColumnDef<PayerScorecard>[] = [
    {
      key: 'payer_reference',
      header: 'Reference',
      cell: (row) => (
        <span className="font-mono text-cyan-400 font-bold hover:underline">
          {row.payer_reference}
        </span>
      ),
    },
    {
      key: 'payer_name',
      header: 'Payer Name',
      cell: (row) => <span className="font-semibold text-slate-100">{row.payer_name}</span>,
    },
    {
      key: 'payer_type',
      header: 'Type',
      cell: (row) => (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
          {row.payer_type}
        </span>
      ),
    },
    {
      key: 'claim_volume',
      header: 'Claims',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-200">{formatNumber(row.claim_volume)}</span>,
    },
    {
      key: 'total_paid',
      header: 'Total Paid',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-emerald-400">{formatCurrency(row.total_paid)}</span>
      ),
    },
    {
      key: 'denial_rate',
      header: 'Denial Rate',
      align: 'right',
      cell: (row) => (
        <span
          className={`font-mono font-bold ${
            row.denial_rate > 0.15 ? 'text-rose-400' : 'text-slate-300'
          }`}
        >
          {formatPercentage(row.denial_rate, true)}
        </span>
      ),
    },
    {
      key: 'average_adjudication_latency_days',
      header: 'Adj. Latency',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-slate-300">{row.average_adjudication_latency_days.toFixed(1)}d</span>
      ),
    },
    {
      key: 'average_payment_latency_days',
      header: 'Pay Latency',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-slate-300">{row.average_payment_latency_days.toFixed(1)}d</span>
      ),
    },
    {
      key: 'timely_filing_compliance_rate',
      header: 'Timely Filing',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-emerald-400">
          {formatPercentage(row.timely_filing_compliance_rate, true)}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <Building2 className="w-5 h-5 text-cyan-400" />
            <span>Payer Operational & Adjudication Scorecards</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Payer efficiency benchmarks, adjudication turnarounds, denial rates, and contractual payment rates.
          </p>
        </div>
      </div>

      <FilterBar
        onReset={() => {
          setSearchQuery('');
          setTypeFilter('');
        }}
      >
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          onClear={() => setSearchQuery('')}
          placeholder="Search by payer name, reference, or type..."
        />

        <SelectFilter
          label="Payer Type"
          value={typeFilter}
          onChange={setTypeFilter}
          options={payerTypes}
          allLabel="All Payer Types"
        />
      </FilterBar>

      {error && (
        <ErrorAlert
          title="Payer Telemetry Error"
          message={error.message}
          requestId={error.requestId}
          onRetry={fetchScorecards}
        />
      )}

      <DataTable
        columns={columns}
        data={filteredScorecards}
        keyExtractor={(p) => p.payer_id}
        isLoading={isLoading}
        emptyTitle="No Payers Found"
        emptyDescription="No payer scorecards match your search filter criteria."
        onRowClick={(row) => navigate(`/payers/${row.payer_id}`)}
      />
    </div>
  );
};
