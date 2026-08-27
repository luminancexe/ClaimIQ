import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from 'recharts';
import { RootCauseItem } from '../../types';
import { cn } from '../../utils/format';

interface ParetoBarChartProps {
  items: RootCauseItem[];
  height?: number;
  className?: string;
}

export const ParetoBarChart: React.FC<ParetoBarChartProps> = ({
  items,
  height = 300,
  className,
}) => {
  if (!items || items.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-xs font-mono">
        No root cause defect data available
      </div>
    );
  }

  const chartData = items.slice(0, 10).map((item) => ({
    name: item.anomaly_code,
    count: item.issue_count,
    cumPercent: item.cumulative_percentage,
    desc: item.description,
  }));

  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="name"
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#94a3b8', fontFamily: 'monospace' }}
            angle={-30}
            textAnchor="end"
          />
          <YAxis
            yAxisId="left"
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'monospace' }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            domain={[0, 100]}
            stroke="#f59e0b"
            tick={{ fontSize: 11, fill: '#f59e0b', fontFamily: 'monospace' }}
            unit="%"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '12px',
              fontFamily: 'monospace',
            }}
          />
          <Legend
            wrapperStyle={{
              fontSize: '11px',
              fontFamily: 'monospace',
              paddingTop: '8px',
            }}
          />
          <ReferenceLine
            yAxisId="right"
            y={80}
            stroke="#f43f5e"
            strokeDasharray="4 4"
            label={{ value: '80% Cutoff', fill: '#f43f5e', fontSize: 10, position: 'top' }}
          />
          <Bar yAxisId="left" dataKey="count" name="Issue Count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="cumPercent"
            name="Cumulative %"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ r: 3, fill: '#f59e0b' }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
