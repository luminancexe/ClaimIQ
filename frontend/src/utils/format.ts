import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format string or number currency into clean $X,XXX.XX display.
 * Preserves Decimal string precision where possible.
 */
export function formatCurrency(amount: string | number | null | undefined): string {
  if (amount === null || amount === undefined || amount === '') {
    return '$0.00';
  }

  const strVal = String(amount).trim();
  const num = parseFloat(strVal);
  if (isNaN(num)) {
    return '$0.00';
  }

  // Use Intl.NumberFormat for clean localized formatting
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

/**
 * Format percentage value (0.0 to 100.0 or ratio 0.0 to 1.0).
 */
export function formatPercentage(val: number | string | null | undefined, isRatio = false): string {
  if (val === null || val === undefined || val === '') {
    return '0.0%';
  }
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) {
    return '0.0%';
  }
  const percentage = isRatio ? num * 100 : num;
  return `${percentage.toFixed(1)}%`;
}

/**
 * Format integer or decimal numbers with thousand separators.
 */
export function formatNumber(val: number | string | null | undefined): string {
  if (val === null || val === undefined || val === '') {
    return '0';
  }
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) {
    return '0';
  }
  return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Format ISO date string into human-readable YYYY-MM-DD or Month DD, YYYY.
 */
export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) {
    return '—';
  }
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) {
      return String(dateStr);
    }
    return d.toISOString().split('T')[0];
  } catch {
    return String(dateStr);
  }
}

/**
 * Format ISO datetime string into YYYY-MM-DD HH:mm:ss.
 */
export function formatDateTime(dateTimeStr: string | null | undefined): string {
  if (!dateTimeStr) {
    return '—';
  }
  try {
    const d = new Date(dateTimeStr);
    if (isNaN(d.getTime())) {
      return String(dateTimeStr);
    }
    return d.toISOString().replace('T', ' ').substring(0, 19);
  } catch {
    return String(dateTimeStr);
  }
}
