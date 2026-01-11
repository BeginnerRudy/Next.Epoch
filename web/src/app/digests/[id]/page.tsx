'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Calendar, FileText, Clock, ExternalLink } from 'lucide-react';
import { getDigest } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { Digest, DigestSection, ContentItem } from '@/types';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { SourceBadge } from '@/components/ui/SourceBadge';

// Mock digest for demo
const mockDigest: Digest = {
  id: 'digest-1',
  type: 'daily',
  title: 'AI Frontier Daily - January 11, 2026',
  summary:
    'Today\'s highlights include breakthrough research on long-context transformers, new open-source agent frameworks, and significant advances in code generation models. The AI community saw three major paper releases from leading research labs, along with several trending repositories gaining significant traction.',
  sections: [
    {
      title: 'Top Papers',
      summary:
        'Key research publications that are shaping the future of AI, focusing on efficiency and reasoning capabilities.',
      items: [
        {
          id: '1',
          type: 'paper',
          source: 'arxiv',
          title: 'Attention Is All You Need: Revisiting Transformers for Long-Range Dependencies',
          summary:
            'Breakthrough paper introducing more efficient attention mechanisms for processing longer sequences.',
          url: 'https://arxiv.org/abs/2401.00001',
          canonical_ref: 'arxiv:2401.00001',
          published_at: new Date(Date.now() - 3600000).toISOString(),
          discovered_at: new Date().toISOString(),
          frontier_score: 0.92,
          field_ids: ['llm'],
          tags: ['transformers', 'attention'],
          authors: [
            { name: 'John Smith', affiliation: 'OpenAI' },
            { name: 'Jane Doe', affiliation: 'Google DeepMind' },
          ],
        },
        {
          id: '2',
          type: 'paper',
          source: 'arxiv',
          title: 'Chain-of-Thought Prompting Elicits Reasoning in Large Language Models',
          summary:
            'Demonstrates how step-by-step reasoning significantly improves LLM performance on complex tasks.',
          url: 'https://arxiv.org/abs/2401.00002',
          canonical_ref: 'arxiv:2401.00002',
          published_at: new Date(Date.now() - 7200000).toISOString(),
          discovered_at: new Date().toISOString(),
          frontier_score: 0.85,
          field_ids: ['llm', 'reasoning'],
          tags: ['chain-of-thought', 'reasoning'],
          authors: [{ name: 'Alice Chen', affiliation: 'Anthropic' }],
        },
      ],
    },
    {
      title: 'Trending Repositories',
      summary: 'Open-source projects gaining momentum in the AI community this week.',
      items: [
        {
          id: '3',
          type: 'repository',
          source: 'github_trending',
          title: 'llama-factory/LLaMA-Factory',
          description:
            'Unified framework for fine-tuning 100+ LLMs with efficient methods like LoRA and QLoRA.',
          url: 'https://github.com/llama-factory/LLaMA-Factory',
          canonical_ref: 'github:llama-factory/LLaMA-Factory',
          published_at: new Date(Date.now() - 43200000).toISOString(),
          discovered_at: new Date().toISOString(),
          frontier_score: 0.78,
          field_ids: ['llm'],
          tags: ['fine-tuning', 'lora'],
          owner: 'llama-factory',
          repo_name: 'LLaMA-Factory',
          language: 'Python',
          stars: 15420,
          forks: 2340,
        },
        {
          id: '4',
          type: 'repository',
          source: 'github_trending',
          title: 'microsoft/autogen',
          description:
            'A framework for building multi-agent conversational AI systems.',
          url: 'https://github.com/microsoft/autogen',
          canonical_ref: 'github:microsoft/autogen',
          published_at: new Date(Date.now() - 86400000).toISOString(),
          discovered_at: new Date().toISOString(),
          frontier_score: 0.72,
          field_ids: ['agents'],
          tags: ['agents', 'multi-agent'],
          owner: 'microsoft',
          repo_name: 'autogen',
          language: 'Python',
          stars: 28500,
          forks: 4200,
        },
      ],
    },
    {
      title: 'Emerging Trends',
      summary:
        'Notable patterns and themes emerging from this week\'s content across the AI landscape.',
      items: [],
    },
  ],
  generated_at: new Date().toISOString(),
  period_start: new Date(Date.now() - 86400000).toISOString(),
  period_end: new Date().toISOString(),
  item_count: 24,
};

function DigestItemCard({ item }: { item: ContentItem }) {
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

      {(item.summary || item.description) && (
        <p className="text-sm text-gray-600 line-clamp-2 mb-2">
          {item.summary || item.description}
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
  return (
    <div className="mb-8">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{section.title}</h3>
      {section.summary && (
        <p className="text-gray-600 mb-4">{section.summary}</p>
      )}
      {section.items.length > 0 ? (
        <div className="space-y-3">
          {section.items.map((item) => (
            <DigestItemCard key={item.id} item={item} />
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

  const content = digest ?? mockDigest;

  const typeColors = {
    daily: 'bg-blue-100 text-blue-700 border-blue-200',
    weekly: 'bg-purple-100 text-purple-700 border-purple-200',
    field: 'bg-green-100 text-green-700 border-green-200',
  };

  const typeLabels = {
    daily: 'Daily Digest',
    weekly: 'Weekly Digest',
    field: 'Field Digest',
  };

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
            className={`text-sm font-medium px-3 py-1 rounded border ${typeColors[content.type]}`}
          >
            {typeLabels[content.type]}
          </span>
          <span className="text-sm text-gray-500 flex items-center gap-1">
            <Clock className="w-4 h-4" />
            Generated {formatDate(content.generated_at)}
          </span>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">{content.title}</h1>

        <div className="flex items-center gap-6 text-sm text-gray-600 mb-4">
          <span className="flex items-center gap-1.5">
            <FileText className="w-4 h-4" />
            {content.item_count} items covered
          </span>
          <span className="flex items-center gap-1.5">
            <Calendar className="w-4 h-4" />
            {formatDate(content.period_start)} - {formatDate(content.period_end)}
          </span>
        </div>

        <p className="text-gray-700 leading-relaxed">{content.summary}</p>
      </div>

      {/* Sections */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {content.sections.map((section, index) => (
          <DigestSectionComponent key={index} section={section} />
        ))}
      </div>

      {/* Demo notice */}
      {error && (
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-700">
            Showing demo digest. Start the backend API for real data.
          </p>
        </div>
      )}
    </div>
  );
}
