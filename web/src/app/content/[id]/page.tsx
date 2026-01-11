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
} from 'lucide-react';
import { getContentItem } from '@/lib/api';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { SourceBadge } from '@/components/ui/SourceBadge';
import { Button, LinkButton } from '@/components/ui/Button';
import { formatDate, formatNumber } from '@/lib/utils';
import { ContentItem, Signal } from '@/types';

// Mock item for demo
const mockItem: ContentItem = {
  id: '1',
  type: 'paper',
  source: 'arxiv',
  title: 'Attention Is All You Need: Revisiting Transformers for Long-Range Dependencies',
  summary:
    'This paper introduces a revolutionary transformer architecture that has become the foundation of modern large language models. The key innovation is the self-attention mechanism which allows the model to weigh the importance of different parts of the input when making predictions.',
  abstract:
    'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.',
  url: 'https://arxiv.org/abs/2401.00001',
  canonical_ref: 'arxiv:2401.00001',
  published_at: new Date(Date.now() - 3600000).toISOString(),
  discovered_at: new Date().toISOString(),
  frontier_score: 0.92,
  score_breakdown: {
    relevance: 0.95,
    importance: 0.88,
    novelty: 0.85,
    recency_boost: 0.92,
    signals: [
      { name: 'category_match', value: 'cs.AI, cs.LG', confidence: 1.0 },
      { name: 'author_authority', value: 'OpenAI, Google DeepMind', confidence: 0.9 },
      { name: 'has_code', value: true, confidence: 1.0 },
      { name: 'keyword_density', value: 0.85, confidence: 0.95 },
      { name: 'citation_potential', value: 'High', confidence: 0.8 },
    ],
  },
  field_ids: ['llm', 'transformers'],
  tags: ['transformers', 'attention', 'nlp', 'deep-learning'],
  authors: [
    { name: 'John Smith', affiliation: 'OpenAI' },
    { name: 'Jane Doe', affiliation: 'Google DeepMind' },
    { name: 'Alice Chen', affiliation: 'Stanford University' },
  ],
  categories: ['cs.AI', 'cs.LG', 'cs.CL'],
  pdf_url: 'https://arxiv.org/pdf/2401.00001.pdf',
};

function SignalDisplay({ signal }: { signal: Signal }) {
  const formatValue = (value: string | number | boolean) => {
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (typeof value === 'number') return `${Math.round(value * 100)}%`;
    return value;
  };

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-600 capitalize">
        {signal.name.replace(/_/g, ' ')}
      </span>
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-gray-900">
          {formatValue(signal.value)}
        </span>
        {signal.confidence && (
          <span className="text-xs text-gray-400">
            ({Math.round(signal.confidence * 100)}% conf)
          </span>
        )}
      </div>
    </div>
  );
}

export default function ContentDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: item, isLoading, error } = useQuery({
    queryKey: ['content', id],
    queryFn: () => getContentItem(id),
    retry: false,
  });

  // Use mock data if API fails
  const content = item ?? mockItem;
  const isPaper = content.type === 'paper';
  const isRepo = content.type === 'repository';

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 bg-gray-200 rounded" />
          <div className="h-12 w-3/4 bg-gray-200 rounded" />
          <div className="h-24 bg-gray-200 rounded" />
          <div className="h-48 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex items-center gap-3">
            <SourceBadge source={content.source} />
            <span className="text-sm text-gray-500">
              {formatDate(content.published_at)}
            </span>
          </div>
          <ScoreBadge score={content.frontier_score} size="lg" showLabel />
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">{content.title}</h1>

        {/* Authors (for papers) */}
        {isPaper && content.authors && content.authors.length > 0 && (
          <div className="flex items-start gap-2 mb-4">
            <Users className="w-5 h-5 text-gray-400 mt-0.5" />
            <div>
              {content.authors.map((author, i) => (
                <span key={i} className="text-gray-700">
                  {author.name}
                  {author.affiliation && (
                    <span className="text-gray-500"> ({author.affiliation})</span>
                  )}
                  {i < content.authors!.length - 1 && ', '}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Repo stats */}
        {isRepo && (
          <div className="flex items-center gap-6 mb-4 text-gray-600">
            {content.stars !== undefined && (
              <span className="flex items-center gap-1.5">
                <Star className="w-5 h-5" />
                {formatNumber(content.stars)} stars
              </span>
            )}
            {content.forks !== undefined && (
              <span className="flex items-center gap-1.5">
                <GitFork className="w-5 h-5" />
                {formatNumber(content.forks)} forks
              </span>
            )}
            {content.language && (
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-primary-500" />
                {content.language}
              </span>
            )}
          </div>
        )}

        {/* Categories */}
        {content.categories && content.categories.length > 0 && (
          <div className="flex items-center gap-2 mb-4">
            <Tag className="w-4 h-4 text-gray-400" />
            {content.categories.map((cat) => (
              <span
                key={cat}
                className="text-sm px-2 py-0.5 bg-primary-100 text-primary-700 rounded"
              >
                {cat}
              </span>
            ))}
          </div>
        )}

        {/* Tags */}
        {content.tags && content.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {content.tags.map((tag) => (
              <span
                key={tag}
                className="text-sm px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
          <a
            href={content.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            View Source
            <ExternalLink className="w-4 h-4" />
          </a>
          {isPaper && content.pdf_url && (
            <a
              href={content.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <FileText className="w-4 h-4" />
              View PDF
            </a>
          )}
        </div>
      </div>

      {/* Summary */}
      {content.summary && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            <h2 className="text-lg font-semibold text-gray-900">AI Summary</h2>
          </div>
          <p className="text-gray-700 leading-relaxed">{content.summary}</p>
        </div>
      )}

      {/* Abstract (for papers) */}
      {isPaper && content.abstract && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Abstract</h2>
          <p className="text-gray-700 leading-relaxed">{content.abstract}</p>
        </div>
      )}

      {/* Score Breakdown */}
      {content.score_breakdown && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-500" />
            <h2 className="text-lg font-semibold text-gray-900">Why This Matters</h2>
          </div>

          {/* Score bars */}
          <div className="space-y-4 mb-6">
            {[
              { label: 'Relevance', value: content.score_breakdown.relevance },
              { label: 'Importance', value: content.score_breakdown.importance },
              { label: 'Novelty', value: content.score_breakdown.novelty },
              { label: 'Recency', value: content.score_breakdown.recency_boost },
            ]
              .filter((s) => s.value !== undefined)
              .map((score) => (
                <div key={score.label}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{score.label}</span>
                    <span className="text-sm text-gray-500">
                      {Math.round(score.value! * 100)}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full transition-all"
                      style={{ width: `${score.value! * 100}%` }}
                    />
                  </div>
                </div>
              ))}
          </div>

          {/* Signals */}
          {content.score_breakdown.signals && content.score_breakdown.signals.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Info className="w-4 h-4 text-gray-400" />
                <h3 className="text-sm font-semibold text-gray-700">Evidence Signals</h3>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                {content.score_breakdown.signals.map((signal, i) => (
                  <SignalDisplay key={i} signal={signal} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Demo notice */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-700">
            Showing demo content. Start the backend API for real data.
          </p>
        </div>
      )}
    </div>
  );
}
