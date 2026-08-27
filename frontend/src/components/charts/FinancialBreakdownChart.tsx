import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';
import { FinancialOverview } from '../../types';
import { cn, formatCurrency } from '../../utils/format';


interface FinancialBreakdownChartProps {
  financial: FinancialOverview;
  height?: number;
  className?: string;
}

export const FinancialBreakdownChart: React.FC<FinancialBreakdownChartProps> = ({
  financial,
  height = 240,
  className,
}) => {
  if (!financial) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-xs font-mono">
        No financial data available
      </div>
    );
  }

  const chartData = [
    { name: 'Total Billed', value: parseFloat(financial.total_billed) || 0, color: '#06b6d4' },
    { name: 'Total Paid', value: parseFloat(financial.total_paid) || 0, color: '#10b981' },
    { name: 'Adjustments', value: parseFloat(financial.total_contractual_adjustments) || 0, color: '#6366f1' },
    { name: 'Patient Resp', value: parseFloat(financial.total_patient_responsibility) || 0, color: '#f59e0b' },
    { name: 'Variance', value: parseFloat(financial.total_variance) || 0, color: '#f43f5e' },
  ];

  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="name"
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#94a3b8', fontFamily: 'monospace' }}
          />
          <YAxis
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'monospace' }}
            tickFormatter={(val) => `$${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
          />
          <Tooltip
            formatter={(value: unknown) => formatCurrency(value as string | number)}
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '12px',
              fontFamily: 'monospace',
            }}
          />
          <Bar dataKey="value" name="Amount" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
