'use client';

import { Suspense, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { getContent } from '@/lib/api';
import { ContentList } from '@/components/content/ContentList';
import { Pagination } from '@/components/ui/Pagination';

const ITEMS_PER_PAGE = 20;

// Category name mapping for better display
const categoryNames: Record<string, string> = {
  'cs.AI': 'Artificial Intelligence',
  'cs.CL': 'Computation and Language (NLP)',
  'cs.CV': 'Computer Vision',
  'cs.LG': 'Machine Learning',
  'cs.RO': 'Robotics',
  'cs.CR': 'Cryptography and Security',
  'cs.IR': 'Information Retrieval',
  'cs.MM': 'Multimedia',
};

export default function ContentPage() {
  return (
    <Suspense fallback={<ContentPageSkeleton />}>
      <ContentPageContent />
    </Suspense>
  );
}

function ContentPageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div>
        <div className="h-8 w-48 bg-gray-200 rounded mb-2" />
        <div className="h-5 w-96 bg-gray-200 rounded" />
      </div>
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg" />
        ))}
      </div>
    </div>
  );
}

function ContentPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const type = searchParams.get('type') || undefined;
  const source = searchParams.get('source') || undefined;
  const field = searchParams.get('field') || undefined;
  const category = searchParams.get('category') || undefined;
  const initialPage = parseInt(searchParams.get('page') || '1', 10);

  const [currentPage, setCurrentPage] = useState(initialPage);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['content', type, source, field, category, currentPage],
    queryFn: () => getContent({
      type,
      source,
      field,
      category,
      page: currentPage,
      per_page: ITEMS_PER_PAGE,
      sort: 'frontier_score',
      order: 'desc',
    }),
    retry: false,
  });

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Update URL
    const params = new URLSearchParams(searchParams.toString());
    if (page > 1) {
      params.set('page', String(page));
    } else {
      params.delete('page');
    }
    router.push(`/content?${params.toString()}`, { scroll: true });
  };

  const getTitle = () => {
    if (type === 'paper') return 'Papers';
    if (type === 'repository') return 'Repositories';
    if (source === 'arxiv') return 'arXiv Papers';
    if (source === 'github_trending') return 'GitHub Trending';
    if (category) return categoryNames[category] || category;
    if (field) return `${field.toUpperCase()} Content`;
    return 'All Content';
  };

  const getDescription = () => {
    if (category) return `Papers and repositories in the ${categoryNames[category] || category} category`;
    if (type === 'paper') return 'Latest research papers from arXiv';
    if (type === 'repository') return 'Trending repositories from GitHub';
    return 'Browse the latest content from the AI frontier';
  };

  const totalItems = data?.pagination?.total_items ?? 0;
  const totalPages = data?.pagination?.total_pages ?? 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{getTitle()}</h1>
          <p className="text-gray-500 mt-1">{getDescription()}</p>
        </div>
        <div className="flex items-center gap-2">
          {isFetching && !isLoading && (
            <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
          )}
          {totalItems > 0 && (
            <span className="text-sm text-gray-500">
              {totalItems.toLocaleString()} items
            </span>
          )}
        </div>
      </div>

      {/* Content List */}
      <ContentList
        items={data?.data ?? []}
        isLoading={isLoading}
        emptyMessage="No content found for the selected filters"
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pt-4 border-t border-gray-200">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
          <p className="text-center text-sm text-gray-500 mt-3">
            Page {currentPage} of {totalPages}
          </p>
        </div>
      )}
    </div>
  );
}
