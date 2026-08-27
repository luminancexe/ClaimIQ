import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  if (pathnames.length === 0 || (pathnames.length === 1 && pathnames[0] === 'dashboard')) {
    return null;
  }

  const formatSegment = (str: string) => {
    return str
      .replace(/-/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  return (
    <nav className="flex items-center space-x-1 text-[11px] font-mono text-slate-400 mb-4">
      <Link
        to="/dashboard"
        className="flex items-center space-x-1 hover:text-slate-200 transition"
      >
        <Home className="w-3.5 h-3.5" />
        <span>Dashboard</span>
      </Link>

      {pathnames.map((value, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <React.Fragment key={to}>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600" />
            {isLast ? (
              <span className="text-cyan-400 font-semibold">{formatSegment(value)}</span>
            ) : (
              <Link to={to} className="hover:text-slate-200 transition">
                {formatSegment(value)}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
