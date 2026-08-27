export interface StatusConfig {
  label: string;
  variant: 'emerald' | 'amber' | 'rose' | 'cyan' | 'indigo' | 'slate';
  bgClass: string;
  textClass: string;
  borderClass: string;
}

export const CLAIM_STATUS_MAP: Record<string, StatusConfig> = {
  Paid: {
    label: 'Paid',
    variant: 'emerald',
    bgClass: 'bg-emerald-500/10',
    textClass: 'text-emerald-400',
    borderClass: 'border-emerald-500/30',
  },
  Accepted: {
    label: 'Accepted',
    variant: 'cyan',
    bgClass: 'bg-cyan-500/10',
    textClass: 'text-cyan-400',
    borderClass: 'border-cyan-500/30',
  },
  Submitted: {
    label: 'Submitted',
    variant: 'indigo',
    bgClass: 'bg-indigo-500/10',
    textClass: 'text-indigo-400',
    borderClass: 'border-indigo-500/30',
  },
  Pending: {
    label: 'Pending',
    variant: 'amber',
    bgClass: 'bg-amber-500/10',
    textClass: 'text-amber-400',
    borderClass: 'border-amber-500/30',
  },
  'Partially Paid': {
    label: 'Partially Paid',
    variant: 'amber',
    bgClass: 'bg-amber-500/10',
    textClass: 'text-amber-300',
    borderClass: 'border-amber-500/30',
  },
  Denied: {
    label: 'Denied',
    variant: 'rose',
    bgClass: 'bg-rose-500/10',
    textClass: 'text-rose-400',
    borderClass: 'border-rose-500/30',
  },
  Rejected: {
    label: 'Rejected',
    variant: 'rose',
    bgClass: 'bg-rose-500/10',
    textClass: 'text-rose-500',
    borderClass: 'border-rose-500/30',
  },
};

export const SEVERITY_MAP: Record<string, StatusConfig> = {
  Critical: {
    label: 'Critical',
    variant: 'rose',
    bgClass: 'bg-rose-500/20',
    textClass: 'text-rose-300 font-semibold',
    borderClass: 'border-rose-500/50',
  },
  High: {
    label: 'High',
    variant: 'rose',
    bgClass: 'bg-rose-500/10',
    textClass: 'text-rose-400',
    borderClass: 'border-rose-500/30',
  },
  Medium: {
    label: 'Medium',
    variant: 'amber',
    bgClass: 'bg-amber-500/10',
    textClass: 'text-amber-400',
    borderClass: 'border-amber-500/30',
  },
  Low: {
    label: 'Low',
    variant: 'cyan',
    bgClass: 'bg-cyan-500/10',
    textClass: 'text-cyan-400',
    borderClass: 'border-cyan-500/30',
  },
};

export const DIMENSION_NAMES: Record<string, string> = {
  Referential: 'Referential Integrity',
  Financial: 'Financial Integrity',
  Completeness: 'Completeness',
  Validity: 'Validity & Conformance',
  Uniqueness: 'Uniqueness',
  Temporal: 'Temporal Consistency',
  Accuracy: 'Accuracy & State Logic',
};
