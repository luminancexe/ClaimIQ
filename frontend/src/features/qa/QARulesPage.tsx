import React, { useState, useEffect, useMemo } from 'react';
import { ShieldCheck } from 'lucide-react';
import { getQARules } from '../../api';
import { QARule, ColumnDef } from '../../types';
import { DataTable } from '../../components/tables/DataTable';
import { SeverityBadge } from '../../components/cards/SeverityBadge';
import { DimensionBadge } from '../../components/cards/DimensionBadge';
import { SearchInput } from '../../components/filters/SearchInput';
import { SelectFilter } from '../../components/filters/SelectFilter';
import { FilterBar } from '../../components/filters/FilterBar';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';

const CATEGORY_OPTIONS = [
  { label: 'Completeness', value: 'COMPLETENESS' },
  { label: 'Validity', value: 'VALIDITY' },
  { label: 'Uniqueness', value: 'UNIQUENESS' },
  { label: 'Financial', value: 'FINANCIAL' },
  { label: 'Temporal', value: 'TEMPORAL' },
  { label: 'Referential', value: 'REFERENTIAL' },
  { label: 'Business Logic', value: 'BUSINESS_LOGIC' },
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

export const QARulesPage: React.FC = () => {
  const [rules, setRules] = useState<QARule[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [dimensionFilter, setDimensionFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRules = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getQARules({
        category: categoryFilter || undefined,
        dimension: dimensionFilter || undefined,
      });
      setRules(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load QA rules catalog');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
  }, [categoryFilter, dimensionFilter]);

  const filteredRules = useMemo(() => {
    if (!searchQuery.trim()) return rules;
    const q = searchQuery.toLowerCase();
    return rules.filter(
      (r) =>
        r.rule_code.toLowerCase().includes(q) ||
        r.rule_name.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q)
    );
  }, [rules, searchQuery]);

  const columns: ColumnDef<QARule>[] = [
    {
      key: 'rule_code',
      header: 'Rule Code',
      cell: (row) => <span className="font-mono text-cyan-400 font-bold">{row.rule_code}</span>,
    },
    {
      key: 'rule_name',
      header: 'Rule Name',
      cell: (row) => <span className="text-slate-100 font-semibold">{row.rule_name}</span>,
    },
    {
      key: 'category_code',
      header: 'Category',
      cell: (row) => (
        <span className="font-mono text-xs text-slate-300">
          {row.category_code || 'STANDARD'}
        </span>
      ),
    },
    {
      key: 'dimension_code',
      header: 'DQ Dimension',
      cell: (row) => <DimensionBadge dimension={row.dimension_code} />,
    },
    {
      key: 'default_severity_code',
      header: 'Severity',
      cell: (row) => <SeverityBadge severity={row.default_severity_code} />,
    },
    {
      key: 'description',
      header: 'Rule Definition & Logic',
      cell: (row) => <span className="text-slate-400 text-xs">{row.description}</span>,
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <span>QA Rule Catalog ({rules.length} Rules)</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Deterministic data quality rules mapped across the 7 canonical DQ dimensions.
          </p>
        </div>
      </div>

      <FilterBar
        onReset={() => {
          setCategoryFilter('');
          setDimensionFilter('');
          setSearchQuery('');
        }}
      >
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          onClear={() => setSearchQuery('')}
          placeholder="Search by code, name, or description..."
        />

        <SelectFilter
          label="Category"
          value={categoryFilter}
          onChange={setCategoryFilter}
          options={CATEGORY_OPTIONS}
          allLabel="All Categories"
        />

        <SelectFilter
          label="Dimension"
          value={dimensionFilter}
          onChange={setDimensionFilter}
          options={DIMENSION_OPTIONS}
          allLabel="All Dimensions"
        />
      </FilterBar>

      {error && <ErrorAlert message={error} onRetry={fetchRules} />}

      <DataTable
        columns={columns}
        data={filteredRules}
        keyExtractor={(r) => r.rule_code}
        isLoading={isLoading}
        emptyTitle="No Rules Found"
        emptyDescription="No QA rules matched your filter criteria."
      />
    </div>
  );
};
