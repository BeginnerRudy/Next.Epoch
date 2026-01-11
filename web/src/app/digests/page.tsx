'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Calendar, FileText, Clock, ChevronRight } from 'lucide-react';
import { getDigests } from '@/lib/api';
import { formatDate, formatRelativeTime } from '@/lib/utils';
import { Digest } from '@/types';

// Mock digests for demo
const mockDigests: Digest[] = [
  {
    id: 'digest-1',
    type: 'daily',
    title: 'AI Frontier Daily - January 11, 2026',
    summary:
      'Today\'s highlights include breakthrough research on long-context transformers, new open-source agent frameworks, and significant advances in code generation models.',
    sections: [],
    generated_at: new Date().toISOString(),
    period_start: new Date(Date.now() - 86400000).toISOString(),
    period_end: new Date().toISOString(),
    item_count: 24,
  },
  {
    id: 'digest-2',
    type: 'daily',
    title: 'AI Frontier Daily - January 10, 2026',
    summary:
      'Key developments in multimodal reasoning, RLHF improvements, and three new trending repositories for LLM fine-tuning.',
    sections: [],
    generated_at: new Date(Date.now() - 86400000).toISOString(),
    period_start: new Date(Date.now() - 172800000).toISOString(),
    period_end: new Date(Date.now() - 86400000).toISOString(),
    item_count: 18,
  },
  {
    id: 'digest-3',
    type: 'weekly',
    title: 'AI Frontier Weekly - Week 2, 2026',
    summary:
      'This week saw major announcements from leading AI labs, including new model releases, safety research, and infrastructure improvements.',
    sections: [],
    generated_at: new Date(Date.now() - 172800000).toISOString(),
    period_start: new Date(Date.now() - 604800000).toISOString(),
    period_end: new Date(Date.now() - 172800000).toISOString(),
    item_count: 87,
  },
  {
    id: 'digest-4',
    type: 'field',
    title: 'AI Agents Field Digest',
    summary:
      'Comprehensive overview of the latest developments in autonomous AI agents, including new frameworks, benchmarks, and real-world applications.',
    sections: [],
    generated_at: new Date(Date.now() - 259200000).toISOString(),
    period_start: new Date(Date.now() - 604800000).toISOString(),
    period_end: new Date(Date.now() - 259200000).toISOString(),
    item_count: 32,
  },
];

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
              className={`text-xs font-medium px-2 py-0.5 rounded border ${typeColors[digest.type]}`}
            >
              {typeLabels[digest.type]}
            </span>
            <span className="text-sm text-gray-500">{formatRelativeTime(digest.generated_at)}</span>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">{digest.title}</h3>

          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{digest.summary}</p>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <FileText className="w-4 h-4" />
              {digest.item_count} items
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

  const digests = data?.data ?? mockDigests;

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
          { id: 'field', label: 'By Field' },
        ].map((tab) => (
          <button
            key={tab.id}
            className="px-4 py-1.5 text-sm font-medium rounded-md transition-colors bg-white text-gray-900 shadow-sm first:bg-white first:shadow-sm"
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Digest List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-5 animate-pulse">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-5 w-16 bg-gray-200 rounded" />
                <div className="h-4 w-24 bg-gray-200 rounded" />
              </div>
              <div className="h-6 w-3/4 bg-gray-200 rounded mb-2" />
              <div className="h-4 w-full bg-gray-200 rounded mb-1" />
              <div className="h-4 w-2/3 bg-gray-200 rounded" />
            </div>
          ))}
        </div>
      ) : digests.length === 0 ? (
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

      {/* Demo notice */}
      {error && (
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-700">
            Showing demo digests. Start the backend API for real data.
          </p>
        </div>
      )}
    </div>
  );
}
