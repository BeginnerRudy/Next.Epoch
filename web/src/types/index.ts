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
  frontier?: number;
  explanation?: string;
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
  categories?: string[];
  // Raw content details (from detail API)
  raw_content?: {
    // Paper fields
    abstract?: string;
    authors?: Author[];
    pdf_url?: string;
    external_id?: string;
    // Repository fields
    description?: string;
    owner?: string;
    name?: string;
    full_name?: string;
    stars?: number;
    forks?: number;
    language?: string;
    topics?: string[];
    homepage?: string;
    trending_rank?: number;
  };
  // Legacy fields (kept for compatibility)
  authors?: Author[];
  abstract?: string;
  pdf_url?: string;
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
  name: string;
  summary: string;
  item_ids: string[];
}

export interface DigestStats {
  total_items: number;
  papers_count: number;
  repos_count: number;
  articles_count: number;
}

export interface Digest {
  id: string;
  type: DigestType;
  title: string;
  executive_summary: string;
  sections: DigestSection[];
  highlights: string[];
  stats: DigestStats;
  generated_at: string;
  period_start: string;
  period_end: string;
  version: string;
}

export interface Pagination {
  page: number;
  per_page: number;
  total_items: number;
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
