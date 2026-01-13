'use client';

import { useQuery } from '@tanstack/react-query';
import { TrendingUp, FileText, GitBranch, RefreshCw, Loader2, Newspaper, Twitter } from 'lucide-react';
import { getContent } from '@/lib/api';
import { ContentList } from '@/components/content/ContentList';
import { Button } from '@/components/ui/Button';

function StatsSkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4 animate-pulse"
        >
          <div className="p-3 rounded-lg bg-gray-200 w-11 h-11" />
          <div>
            <div className="h-7 w-12 bg-gray-200 rounded mb-1" />
            <div className="h-4 w-20 bg-gray-200 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const { data: contentData, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['content', 'dashboard'],
    queryFn: () => getContent({ per_page: 10, sort: 'frontier_score', order: 'desc' }),
    retry: false,
  });

  // Fetch total counts for papers and repos
  const { data: papersData } = useQuery({
    queryKey: ['content', 'papers-count'],
    queryFn: () => getContent({ type: 'paper', per_page: 1 }),
    retry: false,
  });

  const { data: reposData } = useQuery({
    queryKey: ['content', 'repos-count'],
    queryFn: () => getContent({ type: 'repository', per_page: 1 }),
    retry: false,
  });

  // Fetch total count for news articles
  const { data: newsData } = useQuery({
    queryKey: ['content', 'news-count'],
    queryFn: () => getContent({ type: 'article', per_page: 1 }),
    retry: false,
  });

  // Fetch total count for tweets
  const { data: tweetsData } = useQuery({
    queryKey: ['content', 'tweets-count'],
    queryFn: () => getContent({ type: 'social', per_page: 1 }),
    retry: false,
  });

  const items = contentData?.data ?? [];
  const isApiAvailable = !!contentData;
  const totalPapers = papersData?.pagination?.total_items ?? 0;
  const totalRepos = reposData?.pagination?.total_items ?? 0;
  const totalNews = newsData?.pagination?.total_items ?? 0;
  const totalTweets = tweetsData?.pagination?.total_items ?? 0;
  const highImpactCount = items.filter((i) => i.frontier_score >= 0.7).length;

  const stats = [
    {
      label: 'Papers',
      value: totalPapers,
      icon: FileText,
      color: 'text-blue-600 bg-blue-100',
    },
    {
      label: 'Repos',
      value: totalRepos,
      icon: GitBranch,
      color: 'text-purple-600 bg-purple-100',
    },
    {
      label: 'AI News',
      value: totalNews,
      icon: Newspaper,
      color: 'text-indigo-600 bg-indigo-100',
    },
    {
      label: 'Tweets',
      value: totalTweets,
      icon: Twitter,
      color: 'text-sky-600 bg-sky-100',
    },
    {
      label: 'High Impact',
      value: highImpactCount,
      icon: TrendingUp,
      color: 'text-green-600 bg-green-100',
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
              ? 'Latest AI research, repos, news, and influencer tweets'
              : 'Connecting to backend...'}
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => refetch()}
          disabled={isRefetching}
        >
          {isRefetching ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4 mr-2" />
          )}
          Refresh
        </Button>
      </div>

      {/* Stats */}
      {isLoading ? (
        <StatsSkeleton />
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="bg-white rounded-lg border border-gray-200 p-4 flex items-center gap-4 hover:shadow-md transition-shadow"
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
      )}

      {/* Content List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Top Content</h2>
          <span className="text-sm text-gray-500">
            Sorted by Frontier Score
          </span>
        </div>
        <ContentList items={items} isLoading={isLoading} />
      </div>

      {/* API Status */}
      {!isApiAvailable && !isLoading && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="font-medium text-yellow-800">Backend Unavailable</h3>
          <p className="text-sm text-yellow-700 mt-1">
            Could not connect to the backend API. Make sure the API server is running:
          </p>
          <code className="block mt-2 bg-yellow-100 px-3 py-2 rounded text-sm text-yellow-900">
            docker compose up -d
          </code>
        </div>
      )}
    </div>
  );
}
