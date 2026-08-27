import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, PlayCircle, Award, ArrowRight } from 'lucide-react';
import { getDQScores, getQARules } from '../../api';
import { DQScoreSummary, QARule } from '../../types';
import { DimensionBarChart } from '../../components/charts/DimensionBarChart';
import { LoadingSpinner } from '../../components/feedback/LoadingSpinner';
import { ErrorAlert } from '../../components/feedback/ErrorAlert';

export const QAOverviewPage: React.FC = () => {
  const [scores, setScores] = useState<DQScoreSummary | null>(null);
  const [rules, setRules] = useState<QARule[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [scoresData, rulesData] = await Promise.all([
          getDQScores(),
          getQARules(),
        ]);
        setScores(scoresData);
        setRules(rulesData);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load QA telemetry');
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" label="Loading QA Observatory Telemetry..." />;
  }

  if (error) {
    return <ErrorAlert message={error} />;
  }

  const dqScore = scores?.overall_dq_score ?? 100.0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight flex items-center space-x-2.5">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <span>QA Observatory</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Data quality validation rule registry &bull; Execution runs &bull; 7-dimension scoring engine
          </p>
        </div>
      </div>

      {/* Quick Access Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Link
          to="/qa/rules"
          className="group p-5 bg-surface-card border border-slate-800 hover:border-cyan-500/50 rounded-xl transition space-y-3"
        >
          <div className="flex items-center justify-between text-cyan-400">
            <ShieldCheck className="w-5 h-5" />
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-slate-100 font-mono">Rule Catalog</h3>
            <p className="text-xs text-slate-400 mt-1">
              Inspect all <strong className="text-cyan-300">{rules.length}</strong> active QA validation rules.
            </p>
          </div>
        </Link>

        <Link
          to="/qa/runs"
          className="group p-5 bg-surface-card border border-slate-800 hover:border-indigo-500/50 rounded-xl transition space-y-3"
        >
          <div className="flex items-center justify-between text-indigo-400">
            <PlayCircle className="w-5 h-5" />
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-slate-100 font-mono">Execution Runs</h3>
            <p className="text-xs text-slate-400 mt-1">
              Historical QA run telemetry, evaluation durations, and findings.
            </p>
          </div>
        </Link>

        <Link
          to="/qa/scores"
          className="group p-5 bg-surface-card border border-slate-800 hover:border-emerald-500/50 rounded-xl transition space-y-3"
        >
          <div className="flex items-center justify-between text-emerald-400">
            <Award className="w-5 h-5" />
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 transition" />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-slate-100 font-mono">7-Dimension Scores</h3>
            <p className="text-xs text-slate-400 mt-1">
              Current Overall Score: <strong className="text-emerald-400">{dqScore.toFixed(1)}/100</strong>.
            </p>
          </div>
        </Link>
      </div>

      {/* 7-Dimension Score Preview */}
      <div className="bg-surface-card border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 className="text-sm font-semibold text-slate-100 font-mono">
            Dimension Health Breakdown
          </h2>
          <Link to="/qa/scores" className="text-xs font-mono text-cyan-400 hover:underline">
            Detailed Breakdown &rarr;
          </Link>
        </div>

        <DimensionBarChart scores={scores?.dimension_scores || {}} height={260} />
      </div>
    </div>
  );
};
