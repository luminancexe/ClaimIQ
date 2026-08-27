import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { DQTrendPoint } from '../../types';
import { cn } from '../../utils/format';

interface TrendChartProps {
  data: DQTrendPoint[];
  height?: number;
  showDimensions?: boolean;
  className?: string;
}

export const TrendChart: React.FC<TrendChartProps> = ({
  data,
  height = 280,
  showDimensions = false,
  className,
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-xs font-mono">
        No longitudinal trend data available
      </div>
    );
  }

  const chartData = data.map((d) => ({
    time: d.time_bucket,
    score: d.overall_dq_score,
    issues: d.issue_count,
    claims: d.claim_volume,
    ...(showDimensions ? d.dimension_scores : {}),
  }));

  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="time"
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'monospace' }}
          />
          <YAxis
            domain={[0, 100]}
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'monospace' }}
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
          <Line
            type="monotone"
            dataKey="score"
            name="Overall DQ Score"
            stroke="#06b6d4"
            strokeWidth={2.5}
            dot={{ fill: '#06b6d4', r: 3 }}
            activeDot={{ r: 5, fill: '#22d3ee' }}
          />
          {showDimensions && (
            <>
              <Line type="monotone" dataKey="Financial" name="Financial" stroke="#10b981" strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="Referential" name="Referential" stroke="#6366f1" strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="Validity" name="Validity" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
            </>
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
