import { cn } from '@/lib/utils';

interface ScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function ScoreBadge({ score, size = 'md', showLabel = false }: ScoreBadgeProps) {
  const percentage = Math.round(score * 100);

  const getScoreClass = () => {
    if (score >= 0.7) return 'bg-green-100 text-green-800 border-green-300';
    if (score >= 0.4) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-gray-100 text-gray-600 border-gray-300';
  };

  const getLabel = () => {
    if (score >= 0.7) return 'High Impact';
    if (score >= 0.4) return 'Notable';
    return 'Standard';
  };

  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-sm px-2 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 font-medium rounded-full border',
        getScoreClass(),
        sizeClasses[size]
      )}
    >
      <span className="font-bold">{percentage}</span>
      {showLabel && <span className="opacity-75">{getLabel()}</span>}
    </span>
  );
}
