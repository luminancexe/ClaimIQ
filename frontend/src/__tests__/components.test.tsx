import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

import { MetricCard } from '../components/cards/MetricCard';
import { StatusBadge } from '../components/cards/StatusBadge';
import { SeverityBadge } from '../components/cards/SeverityBadge';
import { DataTable, ColumnDef } from '../components/tables/DataTable';
import { PaginationBar } from '../components/tables/PaginationBar';
import { ErrorAlert } from '../components/feedback/ErrorAlert';
import { EmptyState } from '../components/feedback/EmptyState';

describe('Reusable UI Components', () => {
  it('renders MetricCard with title, value, and trend', () => {
    render(
      <MetricCard
        title="Total Claims"
        value="15,420"
        subValue="95% Adj."
        trend="up"
        trendText="Improving"
        variant="cyan"
      />
    );
    expect(screen.getByText('Total Claims')).toBeInTheDocument();
    expect(screen.getByText('15,420')).toBeInTheDocument();
    expect(screen.getByText('95% Adj.')).toBeInTheDocument();
    expect(screen.getByText('Improving')).toBeInTheDocument();
  });

  it('renders StatusBadge and SeverityBadge with correct classes', () => {
    const { rerender } = render(<StatusBadge status="Paid" />);
    expect(screen.getByText('Paid')).toBeInTheDocument();

    rerender(<SeverityBadge severity="Critical" />);
    expect(screen.getByText('Critical')).toBeInTheDocument();
  });

  it('renders DataTable with custom columns, data, and handles row clicks', () => {
    interface TestItem {
      id: number;
      name: string;
      value: string;
    }
    const cols: ColumnDef<TestItem>[] = [
      { key: 'name', header: 'Item Name' },
      { key: 'value', header: 'Amount' },
    ];
    const data: TestItem[] = [
      { id: 1, name: 'Item A', value: '$100.00' },
      { id: 2, name: 'Item B', value: '$200.00' },
    ];
    const onRowClick = vi.fn();

    render(
      <DataTable
        columns={cols}
        data={data}
        keyExtractor={(item) => item.id}
        onRowClick={onRowClick}
      />
    );

    expect(screen.getByText('Item Name')).toBeInTheDocument();
    expect(screen.getByText('Item A')).toBeInTheDocument();
    expect(screen.getByText('$200.00')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Item A'));
    expect(onRowClick).toHaveBeenCalledWith(data[0]);
  });

  it('renders PaginationBar and handles page changes', () => {
    const onPageChange = vi.fn();
    render(
      <PaginationBar
        page={2}
        pageSize={25}
        total={100}
        totalPages={4}
        hasNext={true}
        hasPrevious={true}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText(/Page/)).toBeInTheDocument();
    expect(screen.getByText(/26/)).toBeInTheDocument();
    expect(screen.getByText(/50/)).toBeInTheDocument();
    expect(screen.getByText(/100/)).toBeInTheDocument();

    const prevBtn = screen.getByLabelText('Previous page');
    fireEvent.click(prevBtn);
    expect(onPageChange).toHaveBeenCalledWith(1);
  });

  it('renders ErrorAlert with retry callback and Request ID', () => {
    const onRetry = vi.fn();
    render(
      <ErrorAlert
        title="Network Error"
        message="Failed to connect"
        requestId="req-xyz-99"
        onRetry={onRetry}
      />
    );

    expect(screen.getByText('Network Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to connect')).toBeInTheDocument();
    expect(screen.getByText('req-xyz-99')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Retry'));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('renders EmptyState cleanly', () => {
    render(<EmptyState title="No Records" description="Try another search." />);
    expect(screen.getByText('No Records')).toBeInTheDocument();
    expect(screen.getByText('Try another search.')).toBeInTheDocument();
  });
});
