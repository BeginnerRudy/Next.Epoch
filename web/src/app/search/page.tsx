'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, X } from 'lucide-react';
import { searchContent, getContent } from '@/lib/api';
import { ContentList } from '@/components/content/ContentList';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

const sourceFilters = [
  { id: 'all', label: 'All Sources' },
  { id: 'arxiv', label: 'arXiv' },
  { id: 'github_trending', label: 'GitHub' },
];

const typeFilters = [
  { id: 'all', label: 'All Types' },
  { id: 'paper', label: 'Papers' },
  { id: 'repository', label: 'Repositories' },
];

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="animate-pulse">Loading...</div>}>
      <SearchPageContent />
    </Suspense>
  );
}

function SearchPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const initialQuery = searchParams.get('q') || '';
  const initialSource = searchParams.get('source') || 'all';
  const initialType = searchParams.get('type') || 'all';

  const [query, setQuery] = useState(initialQuery);
  const [source, setSource] = useState(initialSource);
  const [type, setType] = useState(initialType);
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery);

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (debouncedQuery) params.set('q', debouncedQuery);
    if (source !== 'all') params.set('source', source);
    if (type !== 'all') params.set('type', type);

    const newUrl = `/search${params.toString() ? `?${params.toString()}` : ''}`;
    router.replace(newUrl, { scroll: false });
  }, [debouncedQuery, source, type, router]);

  // Search query
  const { data, isLoading } = useQuery({
    queryKey: ['search', debouncedQuery, source, type],
    queryFn: () => {
      if (debouncedQuery.length >= 2) {
        return searchContent({
          q: debouncedQuery,
          source: source !== 'all' ? source : undefined,
          type: type !== 'all' ? type : undefined,
        });
      }
      return getContent({
        source: source !== 'all' ? source : undefined,
        type: type !== 'all' ? type : undefined,
        per_page: 20,
      });
    },
    retry: false,
  });

  const items = data?.data ?? [];
  const hasFilters = source !== 'all' || type !== 'all' || query.length > 0;

  const clearFilters = () => {
    setQuery('');
    setSource('all');
    setType('all');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search</h1>
        <p className="text-gray-500 mt-1">Find papers, repositories, and more</p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by title, author, description..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="mt-4 flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-500">Filters:</span>
          </div>

          {/* Source Filter */}
          <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            {sourceFilters.map((filter) => (
              <button
                key={filter.id}
                onClick={() => setSource(filter.id)}
                className={cn(
                  'px-3 py-1 text-sm rounded-md transition-colors',
                  source === filter.id
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {filter.label}
              </button>
            ))}
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            {typeFilters.map((filter) => (
              <button
                key={filter.id}
                onClick={() => setType(filter.id)}
                className={cn(
                  'px-3 py-1 text-sm rounded-md transition-colors',
                  type === filter.id
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {filter.label}
              </button>
            ))}
          </div>

          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear all
            </Button>
          )}
        </div>
      </div>

      {/* Results */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {debouncedQuery.length >= 2
              ? `Results for "${debouncedQuery}"`
              : 'Browse Content'}
          </h2>
          {data?.pagination && (
            <span className="text-sm text-gray-500">
              {data.pagination.total} items found
            </span>
          )}
        </div>

        <ContentList
          items={items}
          isLoading={isLoading}
          emptyMessage={
            debouncedQuery.length >= 2
              ? `No results found for "${debouncedQuery}"`
              : 'No content available'
          }
        />
      </div>
    </div>
  );
}
