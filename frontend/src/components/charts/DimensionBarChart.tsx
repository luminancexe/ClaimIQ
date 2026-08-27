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
import { DQDimensionScore } from '../../types';
import { cn } from '../../utils/format';

interface DimensionBarChartProps {
  scores: Record<string, DQDimensionScore>;
  height?: number;
  className?: string;
}

export const DimensionBarChart: React.FC<DimensionBarChartProps> = ({
  scores,
  height = 240,
  className,
}) => {
  const chartData = Object.values(scores || {}).map((d) => ({
    name: d.dimension_name || d.dimension_code,
    code: d.dimension_code,
    score: d.raw_score,
    weighted: d.weighted_score,
    issues: d.issues_detected,
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-xs font-mono">
        No dimension scores available
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#10b981';
    if (score >= 70) return '#f59e0b';
    return '#f43f5e';
  };

  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 70, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            type="number"
            domain={[0, 100]}
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#64748b', fontFamily: 'monospace' }}
          />
          <YAxis
            type="category"
            dataKey="code"
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#94a3b8', fontFamily: 'monospace' }}
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
          <Bar dataKey="score" name="Raw Score" radius={[0, 4, 4, 0]}>
            {chartData.map((entry) => (
              <Cell key={`cell-${entry.code}`} fill={getScoreColor(entry.score)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
