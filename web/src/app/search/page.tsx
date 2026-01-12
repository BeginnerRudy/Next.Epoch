'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, X, SortDesc, Loader2 } from 'lucide-react';
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

const sortOptions = [
  { id: 'frontier_score', label: 'Frontier Score' },
  { id: 'published_at', label: 'Date' },
  { id: 'relevance_score', label: 'Relevance' },
];

const categoryFilters = [
  { id: 'all', label: 'All Categories' },
  { id: 'cs.AI', label: 'AI' },
  { id: 'cs.CL', label: 'NLP' },
  { id: 'cs.CV', label: 'Vision' },
  { id: 'cs.LG', label: 'ML' },
  { id: 'cs.RO', label: 'Robotics' },
];

export default function SearchPage() {
  return (
    <Suspense fallback={<SearchPageSkeleton />}>
      <SearchPageContent />
    </Suspense>
  );
}

function SearchPageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div>
        <div className="h-8 w-32 bg-gray-200 rounded mb-2" />
        <div className="h-5 w-64 bg-gray-200 rounded" />
      </div>
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="h-12 bg-gray-200 rounded-lg" />
        <div className="mt-4 flex gap-4">
          <div className="h-8 w-32 bg-gray-200 rounded" />
          <div className="h-8 w-32 bg-gray-200 rounded" />
        </div>
      </div>
    </div>
  );
}

function SearchPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const initialQuery = searchParams.get('q') || '';
  const initialSource = searchParams.get('source') || 'all';
  const initialType = searchParams.get('type') || 'all';
  const initialCategory = searchParams.get('category') || 'all';
  const initialSort = searchParams.get('sort') || 'frontier_score';

  const [query, setQuery] = useState(initialQuery);
  const [source, setSource] = useState(initialSource);
  const [type, setType] = useState(initialType);
  const [category, setCategory] = useState(initialCategory);
  const [sort, setSort] = useState(initialSort);
  const [debouncedQuery, setDebouncedQuery] = useState(initialQuery);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

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
    if (category !== 'all') params.set('category', category);
    if (sort !== 'frontier_score') params.set('sort', sort);

    const newUrl = `/search${params.toString() ? `?${params.toString()}` : ''}`;
    router.replace(newUrl, { scroll: false });
  }, [debouncedQuery, source, type, category, sort, router]);

  // Search query
  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['search', debouncedQuery, source, type, category, sort],
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
        category: category !== 'all' ? category : undefined,
        sort: sort,
        order: 'desc',
        per_page: 20,
      });
    },
    retry: false,
  });

  const items = data?.data ?? [];
  const hasFilters = source !== 'all' || type !== 'all' || category !== 'all' || query.length > 0;
  const activeFiltersCount = [source !== 'all', type !== 'all', category !== 'all'].filter(Boolean).length;

  const clearFilters = () => {
    setQuery('');
    setSource('all');
    setType('all');
    setCategory('all');
    setSort('frontier_score');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Search</h1>
        <p className="text-gray-500 mt-1">Find papers, repositories, and more</p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by title, author, description..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
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

        {/* Quick Filters */}
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>

          {/* Source Filter */}
          <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
            {sourceFilters.map((filter) => (
              <button
                key={filter.id}
                onClick={() => setSource(filter.id)}
                className={cn(
                  'px-3 py-1.5 text-sm rounded-md transition-all',
                  source === filter.id
                    ? 'bg-white text-gray-900 shadow-sm font-medium'
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
                  'px-3 py-1.5 text-sm rounded-md transition-all',
                  type === filter.id
                    ? 'bg-white text-gray-900 shadow-sm font-medium'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {filter.label}
              </button>
            ))}
          </div>

          {/* Advanced Filters Toggle */}
          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className={cn(
              'px-3 py-1.5 text-sm rounded-lg transition-all border',
              showAdvancedFilters || activeFiltersCount > 0
                ? 'bg-primary-50 border-primary-200 text-primary-700'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            )}
          >
            More filters
            {activeFiltersCount > 0 && (
              <span className="ml-1.5 px-1.5 py-0.5 text-xs bg-primary-600 text-white rounded-full">
                {activeFiltersCount}
              </span>
            )}
          </button>

          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear all
            </Button>
          )}
        </div>

        {/* Advanced Filters */}
        {showAdvancedFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200 flex flex-wrap items-center gap-4">
            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Category:</span>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {categoryFilters.map((filter) => (
                  <option key={filter.id} value={filter.id}>
                    {filter.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <SortDesc className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Sort by:</span>
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value)}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {sortOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold text-gray-900">
              {debouncedQuery.length >= 2
                ? `Results for "${debouncedQuery}"`
                : 'Browse Content'}
            </h2>
            {isFetching && !isLoading && (
              <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
            )}
          </div>
          {data?.pagination && (
            <span className="text-sm text-gray-500">
              {data.pagination.total_items.toLocaleString()} items found
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
