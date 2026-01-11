# Next.Epoch - Data Models Specification

> **Version:** 0.2.0
> **Status:** Draft
> **Last Updated:** 2026-01-11

---

## Overview

This document defines all core data models for Next.Epoch. These models serve as the **contract** between all system components.

---

## 1. Source Content Models

### 1.1 Paper

Represents a research paper (primarily from arXiv).

```yaml
Paper:
  id: uuid                       # Internal identifier (UUIDv7)
  source: SourceType            # Origin source
  external_id: string           # ID from source (e.g., arXiv ID "2401.12345")
  canonical_ref: string         # Stable dedupe key (e.g., "arxiv:2401.12345")
  title: string                 # Paper title
  authors: Author[]             # List of authors
  abstract: string              # Paper abstract
  url: string                   # Link to paper
  pdf_url: string | null        # Direct PDF link
  published_at: datetime        # Publication date
  updated_at: datetime | null   # Last update date
  categories: string[]          # arXiv categories (e.g., ["cs.AI", "cs.LG"])
  tags: string[]                # Auto-generated topic tags
  created_at: datetime          # When ingested into our system
```

### 1.2 Article

Represents a news article from AI news sites.

```yaml
Article:
  id: uuid                      # Internal identifier (UUIDv7)
  source: SourceType            # Origin source
  external_id: string | null    # ID from source if available
  canonical_ref: string         # Stable dedupe key (e.g., "verge:<slug>")
  title: string                 # Article title
  author: string | null         # Author name
  content: string               # Full article content
  excerpt: string               # Short excerpt/preview
  url: string                   # Original article URL
  image_url: string | null      # Featured image
  published_at: datetime        # Publication date
  tags: string[]                # Auto-generated topic tags
  created_at: datetime          # When ingested
```

### 1.3 Repository

Represents a GitHub repository.

```yaml
Repository:
  id: uuid                      # Internal identifier (UUIDv7)
  source: SourceType            # Always "github"
  external_id: string           # GitHub repo ID
  canonical_ref: string         # Stable dedupe key (e.g., "github:owner/repo")
  name: string                  # Repo name
  full_name: string             # owner/repo
  description: string | null    # Repo description
  url: string                   # GitHub URL
  homepage: string | null       # Project homepage
  owner: string                 # Owner username
  stars: integer                # Star count
  forks: integer                # Fork count
  language: string | null       # Primary language
  topics: string[]              # GitHub topics
  trending_rank: integer | null # Position in trending
  trending_since: datetime | null
  created_at: datetime          # Repo creation date
  pushed_at: datetime           # Last push date
  ingested_at: datetime         # When ingested
```

### 1.4 SocialPost

Represents a post from Twitter/X.

```yaml
SocialPost:
  id: uuid                      # Internal identifier (UUIDv7)
  source: SourceType            # Always "twitter"
  external_id: string           # Tweet ID
  canonical_ref: string         # Stable dedupe key (e.g., "twitter:<tweet_id>")
  author_handle: string         # @username
  author_name: string           # Display name
  author_verified: boolean      # Verified account
  content: string               # Tweet text
  url: string                   # Tweet URL
  media_urls: string[]          # Attached media
  likes: integer                # Like count
  retweets: integer             # Retweet count
  replies: integer              # Reply count
  posted_at: datetime           # When posted
  tags: string[]                # Auto-generated tags
  created_at: datetime          # When ingested
```

### 1.5 Announcement

Represents official announcements (e.g., from Anthropic).

```yaml
Announcement:
  id: uuid                      # Internal identifier (UUIDv7)
  source: SourceType            # e.g., "anthropic"
  external_id: string | null    # Source ID if available
  canonical_ref: string         # Stable dedupe key (e.g., "anthropic:<slug>")
  title: string                 # Announcement title
  content: string               # Full content
  excerpt: string               # Short summary
  url: string                   # Original URL
  type: AnnouncementType        # Type of announcement
  published_at: datetime        # Publication date
  tags: string[]                # Auto-generated tags
  created_at: datetime          # When ingested
```

---

## 2. Processed Content Models

### 2.1 ContentItem (Unified)

A normalized wrapper for any content type.

```yaml
ContentItem:
  id: uuid                      # Unique identifier (UUIDv7)
  type: ContentType             # paper | article | repository | social | announcement
  source: SourceType            # Origin source
  title: string                 # Content title
  summary: string | null        # AI-generated summary
  url: string                   # Original URL
  relevance_score: float        # 0.0 - 1.0
  importance_score: float       # 0.0 - 1.0 (impact/significance)
  novelty_score: float | null   # 0.0 - 1.0 (new vs baseline)
  frontier_score: float | null  # 0.0 - 1.0 (combined frontier ranking)
  score_breakdown: ScoreBreakdown | null
  tags: string[]                # Topic tags
  categories: string[]          # Broad categories / fields (top-level)
  published_at: datetime        # Original publication
  processed_at: datetime        # When processed by our system
  fields: FieldRef[]            # Mapped fields (may be multiple, with confidence)
  signals: Signal[]             # Evidence signals used for scoring (bounded list)
  provenance: ContentProvenance | null
  raw_content: Paper | Article | Repository | SocialPost | Announcement
```

### 2.2 Field (Taxonomy)

A field represents a stable area of AI used for tracking the frontier.

```yaml
Field:
  id: string                    # Stable ID (e.g., "agents", "llm", "robotics")
  name: string                  # Display name
  description: string | null
  parent_id: string | null      # For hierarchical taxonomy
  aliases: string[]             # Alternate names
  status: FieldStatus
  created_at: datetime
  updated_at: datetime

FieldRef:
  field_id: string
  confidence: float             # 0.0 - 1.0
```

### 2.3 Signals & Scoring

Signals are explainable evidence used to compute scores.

```yaml
Signal:
  key: string                   # e.g., "has_code", "stars_velocity", "mentions"
  value: string | number | boolean
  weight: float | null          # Optional, if used directly in scoring
  source: string | null         # Where the signal came from

ScoreBreakdown:
  relevance: float
  importance: float
  novelty: float | null
  frontier: float | null
  explanation: string | null    # Short human-readable justification

### 2.4 Provenance & Runs

Provenance makes the agent debuggable and auditable.

```yaml
ContentProvenance:
  fetched_at: datetime
  fetched_from: string          # URL or source endpoint
  parser: string                # Parser/normalizer name
  parser_version: string
  content_hash: string | null   # Hash of normalized text if available
  language: string | null

ProcessingRun:
  id: uuid
  type: RunType                 # ingest | enrich | summarize | score | digest
  status: RunStatus             # pending | running | succeeded | failed
  source: SourceType | null
  started_at: datetime
  finished_at: datetime | null
  stats: object | null          # e.g., items_fetched, items_created, llm_calls
  error: string | null
```

### 2.5 Feedback (Evaluation Loop)

Feedback is used to evaluate and improve ranking/summaries.

```yaml
Feedback:
  id: uuid
  content_id: uuid
  kind: FeedbackKind            # relevance | value | summary_quality
  rating: integer               # e.g., 1-5 or -1/0/1 depending on kind
  comment: string | null
  created_at: datetime
  actor: string | null          # API key id, user id, or "anonymous"
```
```

### 2.6 Digest

A curated collection of content for a time period.

```yaml
Digest:
  id: string                    # Unique identifier
  type: DigestType              # flash | daily | weekly
  title: string                 # Digest title
  executive_summary: string     # TL;DR summary
  period_start: datetime        # Coverage start
  period_end: datetime          # Coverage end

  sections:                     # Content organized by section
    - name: string              # Section name (e.g., "Top Papers")
      items: ContentItem[]      # Items in this section
      summary: string           # Section summary

  highlights: string[]          # Key highlights/bullets
  trends: Trend[]               # Detected trends
  stats:                        # Digest statistics
    total_items: integer
    papers_count: integer
    articles_count: integer
    repos_count: integer

  generated_at: datetime        # When digest was created
  version: string               # Digest version
```

### 2.3 Trend

Represents a detected trend in the AI field.

```yaml
Trend:
  id: string                    # Unique identifier
  name: string                  # Trend name (e.g., "Mixture of Experts")
  description: string           # Trend description
  category: string              # Trend category
  momentum: TrendMomentum       # rising | stable | declining
  confidence: float             # 0.0 - 1.0
  first_detected: datetime      # When first noticed
  related_items: string[]       # IDs of related content
  keywords: string[]            # Associated keywords
```

---

## 3. Enums & Types

```yaml
SourceType:
  - arxiv
  - github
  - twitter
  - anthropic
  - verge
  - venturebeat
  - techcrunch
  - custom

ContentType:
  - paper
  - article
  - repository
  - social
  - announcement

DigestType:
  - flash           # Real-time breaking news
  - daily           # Daily summary
  - weekly          # Weekly briefing
  - deep_dive       # On-demand deep analysis

AnnouncementType:
  - product_launch
  - research_release
  - blog_post
  - press_release
  - other

TrendMomentum:
  - rising
  - stable
  - declining

FieldStatus:
  - active
  - deprecated

RunType:
  - ingest
  - enrich
  - summarize
  - score
  - digest

RunStatus:
  - pending
  - running
  - succeeded
  - failed

FeedbackKind:
  - relevance
  - value
  - summary_quality
```

---

## 4. Supporting Models

### 4.1 Author

```yaml
Author:
  name: string                  # Full name
  affiliation: string | null    # Institution
  email: string | null          # Contact email
  url: string | null            # Personal/institutional page
```

### 4.2 Source Configuration

```yaml
SourceConfig:
  id: string                    # Source identifier
  type: SourceType              # Source type
  name: string                  # Display name
  enabled: boolean              # Is active
  refresh_interval: integer     # Minutes between refreshes
  config: object                # Source-specific configuration
  credentials: object | null    # API keys, tokens (encrypted)
  last_fetched: datetime | null # Last successful fetch
  error_count: integer          # Consecutive errors
```

### 4.3 User Preferences (Future)

```yaml
UserPreferences:
  user_id: string               # User identifier
  topics: string[]              # Interested topics
  sources: SourceType[]         # Preferred sources
  digest_frequency: DigestType  # Preferred digest type
  delivery_channels: string[]   # How to receive content
  timezone: string              # User timezone
  language: string              # Preferred language
```

---

## 5. API Response Models

### 5.1 Paginated Response

```yaml
PaginatedResponse<T>:
  data: T[]                     # Array of items
  pagination:
    page: integer               # Current page (1-indexed)
    per_page: integer           # Items per page
    total_items: integer        # Total item count
    total_pages: integer        # Total page count
    has_next: boolean           # Has next page
    has_prev: boolean           # Has previous page
```

### 5.2 API Error

```yaml
APIError:
  error:
    code: string                # Error code (e.g., "NOT_FOUND")
    message: string             # Human-readable message
    details: object | null      # Additional details
  request_id: string            # Request tracking ID
  timestamp: datetime           # When error occurred
```

---

## 6. Database Schema Notes

### Primary Keys
- All `id` fields use UUIDv7 (time-sortable)

### Indexes
- `published_at` - for time-based queries
- `source` - for filtering by source
- `tags` - for topic filtering (GIN index)
- `relevance_score` - for ranking

### Relationships
- `Digest` → `ContentItem` (many-to-many via junction table)
- `ContentItem` → raw content (polymorphic reference)

---

## 7. Validation Rules

| Field | Rule |
|-------|------|
| `id` | Valid UUIDv7 format |
| `url` | Valid HTTP(S) URL |
| `email` | Valid email format |
| `*_score` | Float between 0.0 and 1.0 |
| `*_at` | ISO 8601 datetime |
| `tags` | Non-empty strings, max 50 per item |

---

*This specification defines the data contract. All implementations must conform to these models.*
