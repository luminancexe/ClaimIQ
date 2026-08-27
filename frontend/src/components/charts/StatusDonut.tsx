import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';
import { cn } from '../../utils/format';

interface StatusDonutProps {
  distribution: Record<string, number>;
  height?: number;
  className?: string;
}

const STATUS_COLORS: Record<string, string> = {
  Paid: '#10b981',
  Accepted: '#06b6d4',
  Submitted: '#6366f1',
  Pending: '#f59e0b',
  'Partially Paid': '#fbbf24',
  Denied: '#f43f5e',
  Rejected: '#e11d48',
};

export const StatusDonut: React.FC<StatusDonutProps> = ({
  distribution,
  height = 240,
  className,
}) => {
  const chartData = Object.entries(distribution || {})
    .filter(([, val]) => val > 0)
    .map(([name, value]) => ({
      name,
      value,
    }));

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-xs font-mono">
        No claims status data available
      </div>
    );
  }

  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell
                key={`cell-${entry.name}`}
                fill={STATUS_COLORS[entry.name] || '#94a3b8'}
                stroke="#0f172a"
                strokeWidth={2}
              />
            ))}
          </Pie>
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
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
