import { UserRole } from '../types';

export interface RoleMetadata {
  role: UserRole;
  label: string;
  description: string;
  badgeClass: string;
  allowedRoutes: string[];
}

export const ROLES_METADATA: Record<UserRole, RoleMetadata> = {
  ADMIN: {
    role: 'ADMIN',
    label: 'Administrator',
    description: 'Full operational and analytical system access',
    badgeClass: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
    allowedRoutes: ['/dashboard', '/claims', '/qa', '/analytics', '/providers', '/payers', '/issues'],
  },
  ANALYST: {
    role: 'ANALYST',
    label: 'Data Analyst',
    description: 'Deep analytical, claims exploration, and provider/payer scorecards',
    badgeClass: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',
    allowedRoutes: ['/dashboard', '/claims', '/analytics', '/providers', '/payers', '/issues', '/qa'],
  },
  QA_REVIEWER: {
    role: 'QA_REVIEWER',
    label: 'QA Reviewer',
    description: 'Data quality rule verification, execution runs, and defect telemetry',
    badgeClass: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    allowedRoutes: ['/dashboard', '/qa', '/claims', '/analytics', '/issues'],
  },
  VIEWER: {
    role: 'VIEWER',
    label: 'Read-Only Viewer',
    description: 'Executive dashboard and observational directory overview',
    badgeClass: 'bg-slate-500/20 text-slate-300 border-slate-500/40',
    allowedRoutes: ['/dashboard', '/claims', '/providers', '/payers', '/qa', '/analytics', '/issues'],
  },
};
