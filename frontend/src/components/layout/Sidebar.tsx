import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSpreadsheet,
  ShieldCheck,
  BarChart3,
  UserCheck,
  Building2,
  AlertOctagon,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { MAIN_NAVIGATION, NavItem } from '../../constants/navigation';
import { useAuth } from '../../context/AuthContext';
import { cn } from '../../utils/format';

const ICON_MAP: Record<string, React.FC<{ className?: string }>> = {
  LayoutDashboard,
  FileSpreadsheet,
  ShieldCheck,
  BarChart3,
  UserCheck,
  Building2,
  AlertOctagon,
};

interface SidebarProps {
  onCloseMobile?: () => void;
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile, className }) => {
  const { hasRole } = useAuth();
  const location = useLocation();

  // Track expanded parent items (QA, Analytics)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    'QA Observatory': true,
    'Analytics Suite': true,
  });

  const toggleSection = (name: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [name]: !prev[name],
    }));
  };

  const isChildActive = (item: NavItem): boolean => {
    if (!item.children) return false;
    return item.children.some((child) => location.pathname === child.href);
  };

  return (
    <aside
      className={cn(
        'w-64 bg-surface-sidebar border-r border-slate-800 flex flex-col justify-between select-none',
        className
      )}
    >
      <div className="flex-1 py-4 px-3 overflow-y-auto space-y-1">
        <div className="px-3 pb-2 text-[10px] font-mono font-semibold uppercase tracking-wider text-slate-500">
          Operations Core
        </div>

        {MAIN_NAVIGATION.map((item) => {
          if (item.allowedRoles && !hasRole(...item.allowedRoles)) {
            return null;
          }

          const IconComponent = ICON_MAP[item.iconName] || LayoutDashboard;
          const hasChildren = item.children && item.children.length > 0;
          const isExpanded = !!expandedSections[item.name];
          const activeChild = isChildActive(item);

          if (hasChildren) {
            return (
              <div key={item.name} className="space-y-1">
                <button
                  onClick={() => toggleSection(item.name)}
                  className={cn(
                    'w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition',
                    activeChild
                      ? 'text-cyan-300 bg-cyan-500/10'
                      : 'text-slate-300 hover:text-slate-100 hover:bg-slate-800/60'
                  )}
                >
                  <div className="flex items-center space-x-2.5">
                    <IconComponent
                      className={cn('w-4 h-4', activeChild ? 'text-cyan-400' : 'text-slate-400')}
                    />
                    <span>{item.name}</span>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                  )}
                </button>

                {isExpanded && (
                  <div className="pl-6 pr-2 py-1 space-y-1 border-l border-slate-800 ml-5">
                    {item.children?.map((child) => {
                      if (child.allowedRoles && !hasRole(...child.allowedRoles)) {
                        return null;
                      }
                      return (
                        <NavLink
                          key={child.href}
                          to={child.href}
                          onClick={onCloseMobile}
                          className={({ isActive }) =>
                            cn(
                              'block px-2.5 py-1.5 rounded text-[11px] font-mono transition',
                              isActive
                                ? 'bg-cyan-500/15 text-cyan-300 font-semibold border-r-2 border-cyan-400'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                            )
                          }
                        >
                          {child.name}
                        </NavLink>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          }

          return (
            <NavLink
              key={item.href}
              to={item.href}
              onClick={onCloseMobile}
              className={({ isActive }) =>
                cn(
                  'flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition',
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 font-semibold border-l-2 border-cyan-400 shadow-sm'
                    : 'text-slate-300 hover:text-slate-100 hover:bg-slate-800/60'
                )
              }
            >
              <div className="flex items-center space-x-2.5">
                <IconComponent className="w-4 h-4 text-slate-400 group-hover:text-slate-200" />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-400">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      <div className="p-3 border-t border-slate-800/80 bg-surface-sidebar/90">
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 px-2 py-1">
          <span>MODE: READ-ONLY</span>
          <span className="text-emerald-400">REST ACTIVE</span>
        </div>
      </div>
    </aside>
  );
};
