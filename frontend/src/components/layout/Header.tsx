import React from 'react';
import { ShieldCheck, Activity, LogOut, Menu, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { RoleBadge } from '../cards/RoleBadge';
import { cn } from '../../utils/format';

interface HeaderProps {
  onToggleMobileMenu?: () => void;
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileMenu, className }) => {
  const { user, logout } = useAuth();

  return (
    <header
      className={cn(
        'h-16 px-4 sm:px-6 bg-surface-header/95 border-b border-slate-800 flex items-center justify-between sticky top-0 z-30 backdrop-blur-md',
        className
      )}
    >
      <div className="flex items-center space-x-3">
        {onToggleMobileMenu && (
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shadow-glow-cyan">
            <ShieldCheck className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-base tracking-tight text-slate-100 font-sans">
                Claim<span className="text-cyan-400">IQ</span>
              </span>
              <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                v0.8.0
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono tracking-wider hidden sm:block">
              HEALTHCARE DATA QUALITY CONSOLE
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span>API LIVE</span>
        </div>

        {user && (
          <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
            <div className="hidden sm:flex flex-col items-end">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-medium text-slate-200">{user.username}</span>
                <RoleBadge role={user.role} />
              </div>
              <span className="text-[10px] font-mono text-slate-400">{user.user_id}</span>
            </div>

            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              <User className="w-4 h-4 text-slate-300" />
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              aria-label="Sign Out"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
