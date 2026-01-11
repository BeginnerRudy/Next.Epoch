import { cn } from '@/lib/utils';

interface SourceBadgeProps {
  source: string;
  size?: 'sm' | 'md';
}

export function SourceBadge({ source, size = 'md' }: SourceBadgeProps) {
  const getSourceInfo = () => {
    switch (source) {
      case 'arxiv':
        return { label: 'arXiv', color: 'bg-red-100 text-red-700 border-red-200' };
      case 'github_trending':
        return { label: 'GitHub', color: 'bg-gray-100 text-gray-700 border-gray-200' };
      case 'hacker_news':
        return { label: 'HN', color: 'bg-orange-100 text-orange-700 border-orange-200' };
      default:
        return { label: source, color: 'bg-blue-100 text-blue-700 border-blue-200' };
    }
  };

  const { label, color } = getSourceInfo();

  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-sm px-2 py-0.5',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded border',
        color,
        sizeClasses[size]
      )}
    >
      {label}
    </span>
  );
}
