import Link from 'next/link';
import { ExternalLink, Star, GitFork, Users } from 'lucide-react';
import { ContentItem } from '@/types';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { SourceBadge } from '@/components/ui/SourceBadge';
import { formatRelativeTime, truncate, formatNumber } from '@/lib/utils';

interface ContentCardProps {
  item: ContentItem;
  showSummary?: boolean;
}

export function ContentCard({ item, showSummary = true }: ContentCardProps) {
  const isPaper = item.type === 'paper';
  const isRepo = item.type === 'repository';

  return (
    <article className="content-card bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <SourceBadge source={item.source} size="sm" />
          <span className="text-sm text-gray-500">{formatRelativeTime(item.published_at)}</span>
        </div>
        <ScoreBadge score={item.frontier_score} size="sm" />
      </div>

      {/* Title */}
      <h3 className="mb-2">
        <Link
          href={`/content/${item.id}`}
          className="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors line-clamp-2"
        >
          {item.title}
        </Link>
      </h3>

      {/* Summary or Description */}
      {showSummary && (item.summary || item.abstract || item.description) && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-3">
          {truncate(item.summary || item.abstract || item.description || '', 200)}
        </p>
      )}

      {/* Paper-specific info */}
      {isPaper && item.authors && item.authors.length > 0 && (
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <Users className="w-4 h-4" />
          <span className="line-clamp-1">
            {item.authors.slice(0, 3).map((a) => a.name).join(', ')}
            {item.authors.length > 3 && ` +${item.authors.length - 3} more`}
          </span>
        </div>
      )}

      {/* Repo-specific info */}
      {isRepo && (
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
          {item.stars !== undefined && (
            <span className="flex items-center gap-1">
              <Star className="w-4 h-4" />
              {formatNumber(item.stars)}
            </span>
          )}
          {item.forks !== undefined && (
            <span className="flex items-center gap-1">
              <GitFork className="w-4 h-4" />
              {formatNumber(item.forks)}
            </span>
          )}
          {item.language && (
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-primary-500" />
              {item.language}
            </span>
          )}
        </div>
      )}

      {/* Tags */}
      {item.tags && item.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {item.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full"
            >
              {tag}
            </span>
          ))}
          {item.tags.length > 4 && (
            <span className="text-xs text-gray-400">+{item.tags.length - 4}</span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
        <Link
          href={`/content/${item.id}`}
          className="text-sm font-medium text-primary-600 hover:text-primary-700"
        >
          View Details
        </Link>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          <span>Source</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </article>
  );
}
