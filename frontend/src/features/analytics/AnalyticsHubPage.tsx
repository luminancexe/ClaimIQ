import React from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart3,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Repeat,
  Activity,
  ArrowRight,
} from 'lucide-react';

export const AnalyticsHubPage: React.FC = () => {
  const analyticsModules = [
    {
      title: 'Financial Integrity',
      path: '/analytics/financial',
      icon: DollarSign,
      color: 'emerald',
      description:
        'Reconciliation analysis, contractual adjustments, patient responsibility, and over/underpayment exposure.',
      tag: 'FINANCIAL INTEGRITY',
    },
    {
      title: 'Operational KPIs',
      path: '/analytics/kpis',
      icon: Activity,
      color: 'cyan',
      description:
        'Comprehensive operational indicators spanning claims velocity, payment turnaround, and denial drivers.',
      tag: 'OPERATIONAL METRICS',
    },
    {
      title: 'Longitudinal Trends',
      path: '/analytics/trends',
      icon: TrendingUp,
      color: 'indigo',
      description:
        'Time-series quality score trajectory, score velocity calculations, and historical direction tracking.',
      tag: 'TIME SERIES',
    },
    {
      title: 'Pareto Root Causes',
      path: '/analytics/root-causes',
      icon: AlertTriangle,
      color: 'amber',
      description:
        '80/20 defect driver ranking isolating vital-few anomaly codes driving system-wide issues.',
      tag: 'PARETO 80/20',
    },
    {
      title: 'Recurrence Clusters',
      path: '/analytics/recurrence',
      icon: Repeat,
      color: 'rose',
      description:
        'Identify repeating defect patterns and repeat offender clusters across providers, payers, and claims.',
      tag: 'REPEAT DEFECTS',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            <span>ClaimIQ Analytics Suite</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Analytical intelligence engines spanning financial reconciliation, KPIs, trends, and root cause analysis.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {analyticsModules.map((m) => {
          const Icon = m.icon;
          return (
            <Link
              key={m.path}
              to={m.path}
              className="group bg-surface-card border border-slate-800 hover:border-cyan-500/50 rounded-xl p-5 transition flex flex-col justify-between space-y-4 hover:shadow-glow-cyan/20"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="w-10 h-10 rounded-lg bg-surface-sidebar border border-slate-700 flex items-center justify-center text-cyan-400 group-hover:text-cyan-300">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 uppercase">
                    {m.tag}
                  </span>
                </div>

                <div>
                  <h3 className="font-semibold text-sm text-slate-100 font-mono tracking-wide group-hover:text-cyan-300 transition">
                    {m.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{m.description}</p>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-cyan-400 group-hover:text-cyan-300">
                <span>Launch Telemetry</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};
