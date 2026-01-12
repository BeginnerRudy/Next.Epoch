'use client';

import { useQuery } from '@tanstack/react-query';
import { TrendingUp, FileText, GitBranch, Clock, RefreshCw } from 'lucide-react';
import { getContent, getHealth } from '@/lib/api';
import { ContentList } from '@/components/content/ContentList';
import { Button } from '@/components/ui/Button';
import { formatRelativeTime } from '@/lib/utils';

// Mock data for demo when API is not available
const mockContent = [
  {
    id: '1',
    type: 'paper' as const,
    source: 'arxiv' as const,
    title: 'Attention Is All You Need: Revisiting Transformers for Long-Range Dependencies',
    summary: 'We propose a new architecture that achieves state-of-the-art results on various NLP benchmarks while being significantly more efficient than previous approaches.',
    abstract: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder...',
    url: 'https://arxiv.org/abs/2401.00001',
    canonical_ref: 'arxiv:2401.00001',
    published_at: new Date(Date.now() - 3600000).toISOString(),
    discovered_at: new Date().toISOString(),
    frontier_score: 0.92,
    field_ids: ['llm', 'transformers'],
    tags: ['transformers', 'attention', 'nlp', 'deep-learning'],
    authors: [
      { name: 'John Smith', affiliation: 'OpenAI' },
      { name: 'Jane Doe', affiliation: 'Google DeepMind' },
    ],
    categories: ['cs.AI', 'cs.LG'],
  },
  {
    id: '2',
    type: 'repository' as const,
    source: 'github_trending' as const,
    title: 'llama-factory/LLaMA-Factory',
    description: 'Unified framework for fine-tuning 100+ LLMs with efficient methods like LoRA, QLoRA, and full-parameter training.',
    url: 'https://github.com/llama-factory/LLaMA-Factory',
    canonical_ref: 'github:llama-factory/LLaMA-Factory',
    published_at: new Date(Date.now() - 7200000).toISOString(),
    discovered_at: new Date().toISOString(),
    frontier_score: 0.85,
    field_ids: ['llm', 'fine-tuning'],
    tags: ['llm', 'fine-tuning', 'pytorch', 'deep-learning'],
    owner: 'llama-factory',
    repo_name: 'LLaMA-Factory',
    language: 'Python',
    stars: 15420,
    forks: 2340,
    topics: ['llm', 'fine-tuning', 'lora', 'pytorch'],
  },
  {
    id: '3',
    type: 'paper' as const,
    source: 'arxiv' as const,
    title: 'Chain-of-Thought Prompting Elicits Reasoning in Large Language Models',
    summary: 'We explore how generating a chain of thought—a series of intermediate reasoning steps—significantly improves the ability of large language models to perform complex reasoning.',
    url: 'https://arxiv.org/abs/2401.00002',
    canonical_ref: 'arxiv:2401.00002',
    published_at: new Date(Date.now() - 86400000).toISOString(),
    discovered_at: new Date().toISOString(),
    frontier_score: 0.78,
    field_ids: ['llm', 'reasoning'],
    tags: ['chain-of-thought', 'reasoning', 'prompting'],
    authors: [
      { name: 'Alice Chen', affiliation: 'Anthropic' },
    ],
    categories: ['cs.CL', 'cs.AI'],
  },
  {
    id: '4',
    type: 'repository' as const,
    source: 'github_trending' as const,
    title: 'microsoft/autogen',
    description: 'A programming framework for building AI agents that can collaborate, learn, and solve tasks autonomously.',
    url: 'https://github.com/microsoft/autogen',
    canonical_ref: 'github:microsoft/autogen',
    published_at: new Date(Date.now() - 43200000).toISOString(),
    discovered_at: new Date().toISOString(),
    frontier_score: 0.72,
    field_ids: ['agents'],
    tags: ['agents', 'multi-agent', 'automation'],
    owner: 'microsoft',
    repo_name: 'autogen',
    language: 'Python',
    stars: 28500,
    forks: 4200,
  },
  {
    id: '5',
    type: 'paper' as const,
    source: 'arxiv' as const,
    title: 'Efficient Memory Transformers with Linear Complexity',
    summary: 'We introduce a novel attention mechanism that reduces the quadratic complexity of standard transformers to linear, enabling processing of sequences with millions of tokens.',
    url: 'https://arxiv.org/abs/2401.00003',
    canonical_ref: 'arxiv:2401.00003',
    published_at: new Date(Date.now() - 172800000).toISOString(),
    discovered_at: new Date().toISOString(),
    frontier_score: 0.65,
    field_ids: ['llm', 'efficiency'],
    tags: ['efficiency', 'transformers', 'linear-attention'],
    authors: [
      { name: 'Bob Wilson', affiliation: 'Meta AI' },
      { name: 'Carol Zhang', affiliation: 'Stanford University' },
    ],
    categories: ['cs.LG', 'cs.AI'],
  },
];

export default function DashboardPage() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    retry: false,
  });

  const { data: contentData, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['content', 'dashboard'],
    queryFn: () => getContent({ per_page: 10, sort: 'frontier_score', order: 'desc' }),
    retry: false,
  });

  // Use real data only - no mock fallback
  const items = contentData?.data ?? [];
  const isApiAvailable = !!contentData;

  const stats = [
    {
      label: 'Papers Today',
      value: items.filter((i) => i.type === 'paper').length,
      icon: FileText,
      color: 'text-red-600 bg-red-100',
    },
    {
      label: 'Trending Repos',
      value: items.filter((i) => i.type === 'repository').length,
      icon: GitBranch,
      color: 'text-gray-600 bg-gray-100',
    },
    {
      label: 'High Impact',
      value: items.filter((i) => i.frontier_score >= 0.7).length,
      icon: TrendingUp,
      color: 'text-green-600 bg-green-100',
    },
    {
      label: 'Last Updated',
      value: formatRelativeTime(new Date()),
      icon: Clock,
      color: 'text-blue-600 bg-blue-100',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">
            {isApiAvailable
              ? 'Latest AI research and trending repositories'
              : 'Demo mode - Connect backend for live data'}
          </p>
        </div>
        <Button
          variant="outline"
          icon={RefreshCw}
          onClick={() => refetch()}
          disabled={isRefetching}
          className={isRefetching ? 'animate-spin' : ''}
        >
          Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4"
          >
            <div className={`p-3 rounded-lg ${stat.color}`}>
              <stat.icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-sm text-gray-500">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Content List */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Content</h2>
        <ContentList items={items} isLoading={isLoading} />
      </div>

      {/* API Status */}
      {!isApiAvailable && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-medium text-yellow-800">Demo Mode</h3>
          <p className="text-sm text-yellow-700 mt-1">
            The backend API is not available. Showing sample data. Start the backend with:
          </p>
          <code className="block mt-2 bg-yellow-100 px-3 py-2 rounded text-sm text-yellow-900">
            uvicorn next_epoch.api.main:app --reload
          </code>
        </div>
      )}
    </div>
  );
}
