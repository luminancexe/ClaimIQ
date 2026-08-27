import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserCheck } from 'lucide-react';
import { getProviderAnalytics } from '../../api';
import { ProviderScorecard, ColumnDef } from '../../types';
import { DataTable } from '../../components/tables/DataTable';
import { SearchInput } from '../../components/filters/SearchInput';
import { SelectFilter } from '../../components/filters/SelectFilter';
import { FilterBar } from '../../components/filters/FilterBar';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/format';


export const ProvidersListPage: React.FC = () => {
  const navigate = useNavigate();
  const [scorecards, setScorecards] = useState<ProviderScorecard[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [specialtyFilter, setSpecialtyFilter] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<{ message: string; requestId?: string } | null>(null);

  const fetchScorecards = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProviderAnalytics();
      setScorecards(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to retrieve provider scorecards';
      const reqId = (err as { requestId?: string })?.requestId;
      setError({ message: msg, requestId: reqId });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchScorecards();
  }, []);

  const specialties = useMemo(() => {
    const set = new Set<string>();
    scorecards.forEach((s) => {
      if (s.specialty) set.add(s.specialty);
    });
    return Array.from(set).map((spec) => ({ label: spec, value: spec }));
  }, [scorecards]);

  const filteredScorecards = useMemo(() => {
    return scorecards.filter((s) => {
      const matchesSearch =
        !searchQuery.trim() ||
        s.provider_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.provider_reference.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.specialty.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesSpecialty = !specialtyFilter || s.specialty === specialtyFilter;
      return matchesSearch && matchesSpecialty;
    });
  }, [scorecards, searchQuery, specialtyFilter]);

  const columns: ColumnDef<ProviderScorecard>[] = [
    {
      key: 'provider_reference',
      header: 'Reference',
      cell: (row) => (
        <span className="font-mono text-cyan-400 font-bold hover:underline">
          {row.provider_reference}
        </span>
      ),
    },
    {
      key: 'provider_name',
      header: 'Provider Name',
      cell: (row) => <span className="font-semibold text-slate-100">{row.provider_name}</span>,
    },
    {
      key: 'specialty',
      header: 'Specialty',
      cell: (row) => <span className="text-slate-300 text-xs">{row.specialty}</span>,
    },
    {
      key: 'claim_volume',
      header: 'Claims',
      align: 'right',
      cell: (row) => <span className="font-mono text-slate-200">{formatNumber(row.claim_volume)}</span>,
    },
    {
      key: 'total_billed',
      header: 'Total Billed',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-slate-200">{formatCurrency(row.total_billed)}</span>
      ),
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
      key: 'dq_score',
      header: 'DQ Score',
      align: 'right',
      cell: (row) => (
        <span
          className={`font-mono font-bold ${
            row.dq_score >= 90
              ? 'text-emerald-400'
              : row.dq_score >= 75
              ? 'text-amber-400'
              : 'text-rose-400'
          }`}
        >
          {row.dq_score.toFixed(1)}
        </span>
      ),
    },
    {
      key: 'issue_density',
      header: 'Issue Density',
      align: 'right',
      cell: (row) => (
        <span className="font-mono text-slate-400">{row.issue_density.toFixed(2)}</span>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <UserCheck className="w-5 h-5 text-cyan-400" />
            <span>Provider Quality & Operational Scorecards</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Provider performance metrics, billing accuracy, and quality scorecards across clinical specialties.
          </p>
        </div>
      </div>

      <FilterBar
        onReset={() => {
          setSearchQuery('');
          setSpecialtyFilter('');
        }}
      >
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          onClear={() => setSearchQuery('')}
          placeholder="Search by provider name, ref, or specialty..."
        />

        <SelectFilter
          label="Specialty"
          value={specialtyFilter}
          onChange={setSpecialtyFilter}
          options={specialties}
          allLabel="All Specialties"
        />
      </FilterBar>

      {error && (
        <ErrorAlert
          title="Provider Telemetry Error"
          message={error.message}
          requestId={error.requestId}
          onRetry={fetchScorecards}
        />
      )}

      <DataTable
        columns={columns}
        data={filteredScorecards}
        keyExtractor={(p) => p.provider_id}
        isLoading={isLoading}
        emptyTitle="No Providers Found"
        emptyDescription="No provider scorecards match your search filter criteria."
        onRowClick={(row) => navigate(`/providers/${row.provider_id}`)}
      />
    </div>
  );
};
