import React from 'react';
import { DIMENSION_NAMES } from '../../constants/status';
import { cn } from '../../utils/format';

interface DimensionBadgeProps {
  dimension: string;
  className?: string;
}

export const DimensionBadge: React.FC<DimensionBadgeProps> = ({ dimension, className }) => {
  const fullName = DIMENSION_NAMES[dimension] || dimension;

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium border bg-indigo-500/10 text-indigo-300 border-indigo-500/30 font-mono',
        className
      )}
    >
      {fullName}
    </span>
  );
};
