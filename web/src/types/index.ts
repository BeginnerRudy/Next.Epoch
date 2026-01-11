// Content types matching backend schemas

export type SourceType = 'arxiv' | 'github_trending' | 'hacker_news' | 'twitter' | 'rss';
export type ContentType = 'paper' | 'repository' | 'article' | 'discussion' | 'release';
export type DigestType = 'daily' | 'weekly' | 'field';

export interface Author {
  name: string;
  affiliation?: string;
  url?: string;
}

export interface Signal {
  name: string;
  value: string | number | boolean;
  confidence?: number;
}

export interface ScoreBreakdown {
  relevance: number;
  importance: number;
  novelty?: number;
  recency_boost: number;
  signals: Signal[];
}

export interface ContentItem {
  id: string;
  type: ContentType;
  source: SourceType;
  title: string;
  summary?: string;
  url: string;
  canonical_ref: string;
  published_at: string;
  discovered_at: string;
  frontier_score: number;
  score_breakdown?: ScoreBreakdown;
  field_ids: string[];
  tags: string[];
  // Paper-specific
  authors?: Author[];
  abstract?: string;
  categories?: string[];
  pdf_url?: string;
  // Repository-specific
  owner?: string;
  repo_name?: string;
  description?: string;
  language?: string;
  stars?: number;
  forks?: number;
  topics?: string[];
}

export interface Field {
  id: string;
  name: string;
  description?: string;
  parent_id?: string;
  keywords: string[];
}

export interface DigestSection {
  title: string;
  items: ContentItem[];
  summary?: string;
}

export interface Digest {
  id: string;
  type: DigestType;
  title: string;
  summary: string;
  sections: DigestSection[];
  generated_at: string;
  period_start: string;
  period_end: string;
  item_count: number;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: Pagination;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  timestamp: string;
}

export interface Source {
  id: string;
  type: SourceType;
  name: string;
  enabled: boolean;
}
