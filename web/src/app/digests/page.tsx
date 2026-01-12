'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Calendar, FileText, Clock, ChevronRight, Loader2 } from 'lucide-react';
import { getDigests } from '@/lib/api';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import { Digest } from '@/types';

function DigestCard({ digest }: { digest: Digest }) {
  const typeColors = {
    daily: 'bg-blue-100 text-blue-700 border-blue-200',
    weekly: 'bg-purple-100 text-purple-700 border-purple-200',
    field: 'bg-green-100 text-green-700 border-green-200',
  };

  const typeLabels = {
    daily: 'Daily',
    weekly: 'Weekly',
    field: 'Field',
  };

  return (
    <Link
      href={`/digests/${digest.id}`}
      className="block bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`text-xs font-medium px-2 py-0.5 rounded border ${typeColors[digest.type] || typeColors.daily}`}
            >
              {typeLabels[digest.type] || digest.type}
            </span>
            <span className="text-sm text-gray-500">{formatRelativeTime(digest.generated_at)}</span>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">{digest.title}</h3>

          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{digest.executive_summary}</p>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <FileText className="w-4 h-4" />
              {digest.stats.total_items} items
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              {formatDate(digest.period_start)} - {formatDate(digest.period_end)}
            </span>
          </div>
        </div>

        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
      </div>
    </Link>
  );
}

export default function DigestsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['digests'],
    queryFn: () => getDigests({ per_page: 20 }),
    retry: false,
  });

  const digests = data?.data ?? [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Digests</h1>
          <p className="text-gray-500 mt-1">
            AI-generated summaries of the most important developments
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700">
            Error loading digests. Please try again later.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Digests</h1>
        <p className="text-gray-500 mt-1">
          AI-generated summaries of the most important developments
        </p>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-2 mb-6 bg-gray-100 rounded-lg p-1 w-fit">
        {[
          { id: 'all', label: 'All' },
          { id: 'daily', label: 'Daily' },
          { id: 'weekly', label: 'Weekly' },
        ].map((tab, idx) => (
          <button
            key={tab.id}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
              idx === 0 ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Digest List */}
      {digests.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Clock className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">No digests available yet</p>
          <p className="text-sm text-gray-400 mt-1">
            Digests are generated daily with the latest AI content
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {digests.map((digest) => (
            <DigestCard key={digest.id} digest={digest} />
          ))}
        </div>
      )}
    </div>
  );
}
