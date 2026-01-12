'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { getContent } from '@/lib/api';
import { ContentList } from '@/components/content/ContentList';

export default function ContentPage() {
  return (
    <Suspense fallback={<div className="animate-pulse">Loading...</div>}>
      <ContentPageContent />
    </Suspense>
  );
}

function ContentPageContent() {
  const searchParams = useSearchParams();
  const type = searchParams.get('type') || undefined;
  const source = searchParams.get('source') || undefined;
  const field = searchParams.get('field') || undefined;
  const category = searchParams.get('category') || undefined;

  const { data, isLoading } = useQuery({
    queryKey: ['content', type, source, field, category],
    queryFn: () => getContent({ type, source, field, category, per_page: 20 }),
    retry: false,
  });

  const getTitle = () => {
    if (type === 'paper') return 'Papers';
    if (type === 'repository') return 'Repositories';
    if (source === 'arxiv') return 'arXiv Papers';
    if (source === 'github_trending') return 'GitHub Trending';
    if (category) return `${category} Content`;
    if (field) return `${field.toUpperCase()} Content`;
    return 'All Content';
  };

  const getDescription = () => {
    if (category) return `Papers and repositories in the ${category} category`;
    return `Browse the latest ${type || 'content'} from the AI frontier`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{getTitle()}</h1>
        <p className="text-gray-500 mt-1">{getDescription()}</p>
      </div>

      <ContentList
        items={data?.data ?? []}
        isLoading={isLoading}
        emptyMessage="No content found for the selected filters"
      />
    </div>
  );
}
