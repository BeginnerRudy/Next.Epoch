'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Calendar, FileText, Clock, ExternalLink, Loader2, Sparkles, BookOpen, Code } from 'lucide-react';
import { getDigest, getContentItem } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { Digest, DigestSection, ContentItem } from '@/types';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { SourceBadge } from '@/components/ui/SourceBadge';

function DigestItemCard({ itemId }: { itemId: string }) {
  const { data: item, isLoading } = useQuery({
    queryKey: ['content', itemId],
    queryFn: () => getContentItem(itemId),
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-100 animate-pulse">
        <div className="h-4 w-24 bg-gray-200 rounded mb-2" />
        <div className="h-5 w-3/4 bg-gray-200 rounded mb-2" />
        <div className="h-4 w-full bg-gray-200 rounded" />
      </div>
    );
  }

  if (!item) {
    return null;
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <SourceBadge source={item.source} size="sm" />
        </div>
        <ScoreBadge score={item.frontier_score} size="sm" />
      </div>

      <h4 className="font-medium text-gray-900 mb-1">
        <Link href={`/content/${item.id}`} className="hover:text-primary-600">
          {item.title}
        </Link>
      </h4>

      {item.summary && (
        <p className="text-sm text-gray-600 line-clamp-2 mb-2">
          {item.summary}
        </p>
      )}

      <div className="flex items-center justify-between">
        <Link
          href={`/content/${item.id}`}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          View details
        </Link>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          Source <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
}

function DigestSectionComponent({ section }: { section: DigestSection }) {
  const sectionIcon = section.name.toLowerCase().includes('paper')
    ? <BookOpen className="w-5 h-5 text-blue-600" />
    : <Code className="w-5 h-5 text-purple-600" />;

  return (
    <div className="mb-8 last:mb-0">
      <div className="flex items-center gap-2 mb-3">
        {sectionIcon}
        <h3 className="text-lg font-semibold text-gray-900">{section.name}</h3>
      </div>
      {section.summary && (
        <p className="text-gray-600 mb-4">{section.summary}</p>
      )}
      {section.item_ids.length > 0 ? (
        <div className="space-y-3">
          {section.item_ids.map((itemId) => (
            <DigestItemCard key={itemId} itemId={itemId} />
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm italic">
          No items in this section for the current period.
        </p>
      )}
    </div>
  );
}

export default function DigestDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: digest, isLoading, error } = useQuery({
    queryKey: ['digest', id],
    queryFn: () => getDigest(id),
    retry: false,
  });

  const typeColors: Record<string, string> = {
    daily: 'bg-blue-100 text-blue-700 border-blue-200',
    weekly: 'bg-purple-100 text-purple-700 border-purple-200',
    field: 'bg-green-100 text-green-700 border-green-200',
  };

  const typeLabels: Record<string, string> = {
    daily: 'Daily Digest',
    weekly: 'Weekly Digest',
    field: 'Field Digest',
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !digest) {
    return (
      <div className="max-w-4xl mx-auto">
        <Link href="/digests" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back to Digests
        </Link>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800">Digest not found</h2>
          <p className="text-red-700 mt-2">The digest you're looking for doesn't exist or has been removed.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <Link
        href="/digests"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Digests
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <span
            className={`text-sm font-medium px-3 py-1 rounded border ${typeColors[digest.type] || typeColors.daily}`}
          >
            {typeLabels[digest.type] || digest.type}
          </span>
          <span className="text-sm text-gray-500 flex items-center gap-1">
            <Clock className="w-4 h-4" />
            Generated {formatDate(digest.generated_at)}
          </span>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">{digest.title}</h1>

        <div className="flex items-center gap-6 text-sm text-gray-600 mb-4">
          <span className="flex items-center gap-1.5">
            <FileText className="w-4 h-4" />
            {digest.stats.total_items} items covered
          </span>
          <span className="flex items-center gap-1.5">
            <Calendar className="w-4 h-4" />
            {formatDate(digest.period_start)} - {formatDate(digest.period_end)}
          </span>
        </div>

        <p className="text-gray-700 leading-relaxed">{digest.executive_summary}</p>

        {/* Highlights */}
        {digest.highlights && digest.highlights.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-yellow-500" />
              <h3 className="text-sm font-semibold text-gray-700">Highlights</h3>
            </div>
            <ul className="space-y-1">
              {digest.highlights.map((highlight, i) => (
                <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-primary-500">•</span>
                  {highlight}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Sections */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {digest.sections.map((section, index) => (
          <DigestSectionComponent key={index} section={section} />
        ))}
      </div>
    </div>
  );
}
