import Link from 'next/link';
import { ExternalLink, Star, GitFork, Users, Rss, Building2 } from 'lucide-react';
import { ContentItem } from '@/types';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { SourceBadge } from '@/components/ui/SourceBadge';
import { formatRelativeTime, truncate, formatNumber, formatDate } from '@/lib/utils';

interface ContentCardProps {
  item: ContentItem;
  showSummary?: boolean;
}

// Get content type label for display
function getContentTypeLabel(type: string): string {
  switch (type) {
    case 'article': return 'News';
    case 'application': return 'Product Launch';
    case 'case_study': return 'Case Study';
    default: return type;
  }
}

export function ContentCard({ item, showSummary = true }: ContentCardProps) {
  const isPaper = item.type === 'paper';
  const isRepo = item.type === 'repository';
  const isArticle = item.type === 'article' || item.type === 'application' || item.type === 'case_study';

  // Tooltip text explaining what the time means
  const exactTime = formatDate(item.published_at);
  const timeTooltip = isPaper
    ? `Published: ${exactTime}`
    : isArticle
    ? `Published: ${exactTime}`
    : `Discovered from GitHub Trending: ${exactTime}`;

  // Get source link text
  const getSourceLinkText = () => {
    if (isPaper) return 'arXiv';
    if (isRepo) return 'GitHub';
    if (item.source === 'venturebeat') return 'VentureBeat';
    if (item.source === 'techcrunch') return 'TechCrunch';
    return 'Read Article';
  };

  return (
    <article className="content-card bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <SourceBadge source={item.source} size="sm" />
          {isArticle && (
            <span className="text-xs px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full font-medium">
              {getContentTypeLabel(item.type)}
            </span>
          )}
          <span className="relative group">
            <span className="text-sm text-gray-500 cursor-help border-b border-dotted border-gray-400">
              {formatRelativeTime(item.published_at)}
            </span>
            <span className="absolute left-0 top-full mt-1 z-50 hidden group-hover:block px-2 py-1 text-xs text-white bg-gray-800 rounded shadow-lg whitespace-nowrap">
              {timeTooltip}
            </span>
          </span>
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

      {/* Article-specific info */}
      {isArticle && (
        <div className="flex items-center gap-3 text-sm text-gray-500 mb-3">
          <span className="flex items-center gap-1">
            <Rss className="w-4 h-4 text-indigo-500" />
            <span className="text-indigo-600 font-medium">AI News</span>
          </span>
          {item.categories && item.categories.length > 0 && (
            <span className="flex items-center gap-1">
              <Building2 className="w-4 h-4" />
              {item.categories[0]}
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
          <span>{getSourceLinkText()}</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </article>
  );
}
