import { UserRole } from '../types';

export interface NavItem {
  name: string;
  href: string;
  iconName: string;
  badge?: string;
  allowedRoles?: UserRole[];
  children?: Array<{
    name: string;
    href: string;
    allowedRoles?: UserRole[];
  }>;
}

export const MAIN_NAVIGATION: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    iconName: 'LayoutDashboard',
  },
  {
    name: 'Claims Explorer',
    href: '/claims',
    iconName: 'FileSpreadsheet',
  },
  {
    name: 'QA Observatory',
    href: '/qa',
    iconName: 'ShieldCheck',
    children: [
      { name: 'Rules Catalog', href: '/qa/rules' },
      { name: 'Execution Runs', href: '/qa/runs' },
      { name: 'DQ Scores', href: '/qa/scores' },
    ],
  },
  {
    name: 'Analytics Suite',
    href: '/analytics',
    iconName: 'BarChart3',
    children: [
      { name: 'Overview', href: '/analytics' },
      { name: 'Financial Integrity', href: '/analytics/financial' },
      { name: 'Operational KPIs', href: '/analytics/kpis' },
      { name: 'Longitudinal Trends', href: '/analytics/trends' },
      { name: 'Pareto Root Causes', href: '/analytics/root-causes' },
      { name: 'Recurrence Clusters', href: '/analytics/recurrence' },
    ],
  },
  {
    name: 'Providers',
    href: '/providers',
    iconName: 'UserCheck',
  },
  {
    name: 'Payers',
    href: '/payers',
    iconName: 'Building2',
  },
  {
    name: 'Issues Explorer',
    href: '/issues',
    iconName: 'AlertOctagon',
  },
];
