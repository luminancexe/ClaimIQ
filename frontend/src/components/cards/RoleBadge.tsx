import React from 'react';
import { UserRole } from '../../types';
import { ROLES_METADATA } from '../../constants/roles';
import { cn } from '../../utils/format';

interface RoleBadgeProps {
  role: UserRole;
  className?: string;
}

export const RoleBadge: React.FC<RoleBadgeProps> = ({ role, className }) => {
  const meta = ROLES_METADATA[role] || {
    label: role,
    badgeClass: 'bg-slate-800 text-slate-300 border-slate-700',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold border uppercase tracking-wider font-mono',
        meta.badgeClass,
        className
      )}
    >
      {meta.label}
    </span>
  );
};
