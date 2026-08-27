import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  formatPercentage,
  formatNumber,
  formatDate,
  formatDateTime,
} from '../utils/format';

describe('Format Utilities', () => {
  it('formats currency correctly from strings and numbers preserving precision', () => {
    expect(formatCurrency('1250.50')).toBe('$1,250.50');
    expect(formatCurrency(1250.5)).toBe('$1,250.50');
    expect(formatCurrency('0.00')).toBe('$0.00');
    expect(formatCurrency(null)).toBe('$0.00');
    expect(formatCurrency(undefined)).toBe('$0.00');
  });

  it('formats percentages correctly with ratios and percentage scales', () => {
    expect(formatPercentage(0.852, true)).toBe('85.2%');
    expect(formatPercentage(85.2, false)).toBe('85.2%');
    expect(formatPercentage('94.55', false)).toBe('94.5%');
    expect(formatPercentage(null)).toBe('0.0%');
  });

  it('formats numbers with commas', () => {
    expect(formatNumber(15000)).toBe('15,000');
    expect(formatNumber('1234567')).toBe('1,234,567');
    expect(formatNumber(0)).toBe('0');
  });

  it('formats ISO dates and datetimes safely', () => {
    expect(formatDate('2026-03-15T12:00:00Z')).toBe('2026-03-15');
    expect(formatDate(null)).toBe('—');
    expect(formatDateTime('2026-03-15T14:30:00Z')).toContain('2026-03-15');
    expect(formatDateTime(null)).toBe('—');
  });
});
