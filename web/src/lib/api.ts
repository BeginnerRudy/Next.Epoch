import { ContentItem, Digest, Field, PaginatedResponse, HealthResponse, Source } from '@/types';

const API_BASE = '/api/v1';

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Health
export async function getHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>('/health');
}

// Content
export async function getContent(params?: {
  source?: string;
  type?: string;
  field?: string;
  category?: string;
  page?: number;
  per_page?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}): Promise<PaginatedResponse<ContentItem>> {
  const searchParams = new URLSearchParams();
  if (params?.source) searchParams.set('source', params.source);
  if (params?.type) searchParams.set('type', params.type);
  if (params?.field) searchParams.set('field', params.field);
  if (params?.category) searchParams.set('category', params.category);
  if (params?.page) searchParams.set('page', String(params.page));
  if (params?.per_page) searchParams.set('per_page', String(params.per_page));
  if (params?.sort) searchParams.set('sort', params.sort);
  if (params?.order) searchParams.set('order', params.order);

  const query = searchParams.toString();
  return fetchApi<PaginatedResponse<ContentItem>>(`/content${query ? `?${query}` : ''}`);
}

export async function getContentItem(id: string): Promise<ContentItem> {
  return fetchApi<ContentItem>(`/content/${id}`);
}

export async function searchContent(params: {
  q: string;
  source?: string;
  type?: string;
  page?: number;
  per_page?: number;
}): Promise<PaginatedResponse<ContentItem>> {
  const searchParams = new URLSearchParams();
  searchParams.set('q', params.q);
  if (params.source) searchParams.set('source', params.source);
  if (params.type) searchParams.set('type', params.type);
  if (params.page) searchParams.set('page', String(params.page));
  if (params.per_page) searchParams.set('per_page', String(params.per_page));

  return fetchApi<PaginatedResponse<ContentItem>>(`/content/search?${searchParams.toString()}`);
}

// Digests
export async function getDigests(params?: {
  type?: string;
  page?: number;
  per_page?: number;
}): Promise<PaginatedResponse<Digest>> {
  const searchParams = new URLSearchParams();
  if (params?.type) searchParams.set('type', params.type);
  if (params?.page) searchParams.set('page', String(params.page));
  if (params?.per_page) searchParams.set('per_page', String(params.per_page));

  const query = searchParams.toString();
  return fetchApi<PaginatedResponse<Digest>>(`/digests${query ? `?${query}` : ''}`);
}

export async function getDigest(id: string): Promise<Digest> {
  return fetchApi<Digest>(`/digests/${id}`);
}

export async function getLatestDigest(type: string = 'daily'): Promise<Digest> {
  return fetchApi<Digest>(`/digests/latest?type=${type}`);
}

// Fields
export async function getFields(): Promise<Field[]> {
  return fetchApi<Field[]>('/fields');
}

export async function getField(id: string): Promise<Field> {
  return fetchApi<Field>(`/fields/${id}`);
}

// Sources
export async function getSources(): Promise<Source[]> {
  return fetchApi<Source[]>('/sources');
}

export async function refreshSource(sourceId: string): Promise<{ job_id: string; message: string }> {
  return fetchApi(`/sources/${sourceId}/refresh`, { method: 'POST' });
}
