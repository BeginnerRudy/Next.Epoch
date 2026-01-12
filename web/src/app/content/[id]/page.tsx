'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  ExternalLink,
  Star,
  GitFork,
  Users,
  Calendar,
  FileText,
  Tag,
  TrendingUp,
  Lightbulb,
  Info,
  Award,
  Code,
  BookOpen,
  Loader2,
  Globe,
} from 'lucide-react';
import { getContentItem } from '@/lib/api';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { SourceBadge } from '@/components/ui/SourceBadge';
import { formatDate, formatNumber } from '@/lib/utils';
import { ContentItem } from '@/types';

function SignalCard({ signalKey, value, source }: { signalKey: string; value: string | number | boolean; source?: string }) {
  const formatValue = (val: string | number | boolean) => {
    if (typeof val === 'boolean') return val ? 'Yes' : 'No';
    if (typeof val === 'number') {
      if (val > 1000) return formatNumber(val);
      if (val <= 1) return `${Math.round(val * 100)}%`;
      return val.toString();
    }
    return val;
  };

  const getSignalIcon = (key: string) => {
    if (key.includes('star')) return <Star className="w-4 h-4" />;
    if (key.includes('code')) return <Code className="w-4 h-4" />;
    if (key.includes('trending')) return <TrendingUp className="w-4 h-4" />;
    if (key.includes('author')) return <Users className="w-4 h-4" />;
    return <Info className="w-4 h-4" />;
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <div className="text-gray-400">{getSignalIcon(signalKey)}</div>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-700 capitalize">
          {signalKey.replace(/_/g, ' ')}
        </p>
        {source && <p className="text-xs text-gray-400">{source}</p>}
      </div>
      <span className="text-sm font-semibold text-gray-900">{formatValue(value)}</span>
    </div>
  );
}

export default function ContentDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: content, isLoading, error } = useQuery({
    queryKey: ['content', id],
    queryFn: () => getContentItem(id),
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="max-w-4xl mx-auto">
        <Link href="/" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800">Content not found</h2>
          <p className="text-red-700 mt-2">The content you're looking for doesn't exist or has been removed.</p>
        </div>
      </div>
    );
  }

  const isPaper = content.type === 'paper';
  const isRepo = content.type === 'repository';
  const raw = content.raw_content;

  // Get data from raw_content or fallback to top-level fields
  const abstract = raw?.abstract || content.abstract;
  const authors = raw?.authors || content.authors || [];
  const pdfUrl = raw?.pdf_url || content.pdf_url;
  const stars = raw?.stars ?? content.stars;
  const forks = raw?.forks ?? content.forks;
  const language = raw?.language || content.language;
  const topics = raw?.topics || content.topics || [];
  const description = raw?.description || content.description || content.summary;
  const trendingRank = raw?.trending_rank;
  const homepage = raw?.homepage;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back Button */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      {/* Main Header Card */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {/* Score Banner */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SourceBadge source={content.source} />
            <span className="text-primary-100 text-sm">
              {formatDate(content.published_at)}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-white text-sm font-medium">Frontier Score</span>
            <div className="bg-white/20 rounded-lg px-3 py-1">
              <span className="text-white text-lg font-bold">
                {Math.round(content.frontier_score * 100)}
              </span>
            </div>
          </div>
        </div>

        <div className="p-6">
          {/* Title */}
          <h1 className="text-2xl font-bold text-gray-900 mb-4">{content.title}</h1>

          {/* Paper Authors */}
          {isPaper && authors.length > 0 && (
            <div className="flex items-start gap-3 mb-4 p-4 bg-blue-50 rounded-lg">
              <Users className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-blue-900 mb-1">Authors</p>
                <p className="text-sm text-blue-700">
                  {authors.map((author, i) => (
                    <span key={i}>
                      {author.name}
                      {author.affiliation && (
                        <span className="text-blue-500"> ({author.affiliation})</span>
                      )}
                      {i < authors.length - 1 && ', '}
                    </span>
                  ))}
                </p>
              </div>
            </div>
          )}

          {/* Repository Stats */}
          {isRepo && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              {stars !== undefined && (
                <div className="flex items-center gap-2 p-3 bg-yellow-50 rounded-lg">
                  <Star className="w-5 h-5 text-yellow-600" />
                  <div>
                    <p className="text-lg font-bold text-yellow-900">{formatNumber(stars)}</p>
                    <p className="text-xs text-yellow-700">Stars</p>
                  </div>
                </div>
              )}
              {forks !== undefined && (
                <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                  <GitFork className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="text-lg font-bold text-green-900">{formatNumber(forks)}</p>
                    <p className="text-xs text-green-700">Forks</p>
                  </div>
                </div>
              )}
              {language && (
                <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg">
                  <Code className="w-5 h-5 text-purple-600" />
                  <div>
                    <p className="text-sm font-bold text-purple-900">{language}</p>
                    <p className="text-xs text-purple-700">Language</p>
                  </div>
                </div>
              )}
              {trendingRank && (
                <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-orange-600" />
                  <div>
                    <p className="text-lg font-bold text-orange-900">#{trendingRank}</p>
                    <p className="text-xs text-orange-700">Trending</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Categories */}
          {content.categories && content.categories.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap mb-4">
              <Tag className="w-4 h-4 text-gray-400" />
              {content.categories.map((cat) => (
                <span
                  key={cat}
                  className="text-sm px-3 py-1 bg-primary-100 text-primary-700 rounded-full font-medium"
                >
                  {cat}
                </span>
              ))}
            </div>
          )}

          {/* Topics */}
          {topics.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {topics.map((topic) => (
                <span
                  key={topic}
                  className="text-sm px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
                >
                  {topic}
                </span>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-gray-200">
            <a
              href={content.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              {isPaper ? <BookOpen className="w-4 h-4" /> : <Code className="w-4 h-4" />}
              {isPaper ? 'View on arXiv' : 'View on GitHub'}
              <ExternalLink className="w-4 h-4" />
            </a>
            {isPaper && pdfUrl && (
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                <FileText className="w-4 h-4" />
                Download PDF
              </a>
            )}
            {isRepo && homepage && (
              <a
                href={homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                <Globe className="w-4 h-4" />
                Website
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Abstract (for papers) */}
      {isPaper && abstract && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Abstract</h2>
          </div>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">{abstract}</p>
        </div>
      )}

      {/* Description (for repos) */}
      {isRepo && description && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            <h2 className="text-lg font-semibold text-gray-900">Description</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">{description}</p>
        </div>
      )}

      {/* Why This Matters - Score Analysis */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Award className="w-5 h-5 text-green-600" />
          <h2 className="text-lg font-semibold text-gray-900">Why This Matters</h2>
        </div>

        {/* Score Bars */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {[
            { label: 'Relevance', value: content.score_breakdown?.relevance, color: 'bg-blue-500' },
            { label: 'Importance', value: content.score_breakdown?.importance, color: 'bg-green-500' },
            { label: 'Novelty', value: content.score_breakdown?.novelty, color: 'bg-purple-500' },
            { label: 'Recency', value: content.score_breakdown?.recency_boost, color: 'bg-orange-500' },
          ]
            .filter((s) => s.value !== undefined && s.value !== null)
            .map((score) => (
              <div key={score.label} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{score.label}</span>
                  <span className="text-sm font-bold text-gray-900">
                    {Math.round(score.value! * 100)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${score.color} rounded-full transition-all`}
                    style={{ width: `${score.value! * 100}%` }}
                  />
                </div>
              </div>
            ))}
        </div>

        {/* Explanation */}
        {content.score_breakdown?.explanation && (
          <div className="bg-green-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-green-800">
              <span className="font-semibold">Analysis: </span>
              {content.score_breakdown.explanation}
            </p>
          </div>
        )}

        {/* Signals Grid */}
        {content.score_breakdown?.signals && content.score_breakdown.signals.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Info className="w-4 h-4" />
              Evidence Signals
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {content.score_breakdown.signals.map((signal, i) => (
                <SignalCard
                  key={i}
                  signalKey={signal.name}
                  value={signal.value}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
