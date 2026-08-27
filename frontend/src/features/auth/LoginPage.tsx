import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, Lock, User, ArrowRight, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState<string>('admin');
  const [password, setPassword] = useState<string>('Admin@123');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [loginError, setLoginError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as { from?: string })?.from || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setLoginError('Please enter both username and password');
      return;
    }

    setIsSubmitting(true);
    setLoginError(null);

    try {
      await login({ username, password });
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Authentication failed';
      setLoginError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const setDevAccount = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setLoginError(null);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center p-4 selection:bg-cyan-500/30 selection:text-cyan-200">
      <div className="w-full max-w-md space-y-6">
        {/* Header Branding */}
        <div className="text-center space-y-2">
          <div className="inline-flex w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-indigo-600 items-center justify-center shadow-glow-cyan mb-2">
            <ShieldCheck className="w-7 h-7 text-slate-950 font-bold" />
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight font-sans">
            Claim<span className="text-cyan-400">IQ</span>
          </h1>
          <p className="text-xs font-mono tracking-widest text-slate-400 uppercase">
            Healthcare Claims Data Quality Console
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-surface-card border border-slate-800 rounded-xl p-6 shadow-2xl backdrop-blur-md space-y-5">
          <div className="border-b border-slate-800 pb-3">
            <h2 className="text-sm font-semibold text-slate-200 tracking-wide">
              Operator Authentication
            </h2>
            <p className="text-xs text-slate-400">
              Sign in with your ClaimIQ credentials to access telemetry.
            </p>
          </div>

          {loginError && (
            <div className="flex items-center space-x-2 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{loginError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">
                Username
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. admin"
                  className="w-full bg-surface-sidebar border border-slate-700/80 focus:border-cyan-500 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-slate-400 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-surface-sidebar border border-slate-700/80 focus:border-cyan-500 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 text-slate-950 font-semibold text-xs font-mono uppercase tracking-wider rounded-lg shadow-glow-cyan transition flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Development Test Presets */}
          <div className="pt-4 border-t border-slate-800/80 space-y-2">
            <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block">
              Development Test Accounts
            </span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setDevAccount('admin', 'Admin@123')}
                className="px-2 py-1.5 rounded bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 text-[11px] font-mono text-left transition flex items-center justify-between"
              >
                <span>admin</span>
                <span className="text-[9px] px-1 bg-cyan-500/20 text-cyan-400 rounded">ADMIN</span>
              </button>
              <button
                type="button"
                onClick={() => setDevAccount('analyst', 'Analyst@123')}
                className="px-2 py-1.5 rounded bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 text-[11px] font-mono text-left transition flex items-center justify-between"
              >
                <span>analyst</span>
                <span className="text-[9px] px-1 bg-indigo-500/20 text-indigo-400 rounded">ANALYST</span>
              </button>
              <button
                type="button"
                onClick={() => setDevAccount('qa_reviewer', 'QaReviewer@123')}
                className="px-2 py-1.5 rounded bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 text-[11px] font-mono text-left transition flex items-center justify-between"
              >
                <span>qa_reviewer</span>
                <span className="text-[9px] px-1 bg-emerald-500/20 text-emerald-400 rounded">QA</span>
              </button>
              <button
                type="button"
                onClick={() => setDevAccount('viewer', 'Viewer@123')}
                className="px-2 py-1.5 rounded bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 text-slate-300 text-[11px] font-mono text-left transition flex items-center justify-between"
              >
                <span>viewer</span>
                <span className="text-[9px] px-1 bg-slate-500/20 text-slate-400 rounded">VIEWER</span>
              </button>
            </div>
          </div>
        </div>

        <div className="text-center text-[11px] font-mono text-slate-500">
          ClaimIQ Operations System &bull; Read-Only Session Invariant Active
        </div>
      </div>
    </div>
  );
};
