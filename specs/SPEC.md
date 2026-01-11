# Next.Epoch - Product Specification

> **Version:** 0.2.0
> **Status:** Draft
> **Last Updated:** 2026-01-11

---

## 1. Vision & Mission

### Vision
Become the definitive AI frontier intelligence platform that empowers researchers, engineers, and enthusiasts to stay ahead of the rapidly evolving AI landscape.

### Mission
**Next.Epoch** is an intelligent agent that continuously tracks, curates, and summarizes the cutting edge of AI research and development, delivering actionable insights through multiple channels.

### Tagline
*"Your window into the next epoch of AI."*

---

## 2. Problem Statement

The AI field moves at unprecedented speed:
- **100+ papers** published daily on arXiv (cs.AI, cs.LG, cs.CL)
- **Fragmented sources** — research, news, social media, code repos
- **Signal-to-noise ratio** is extremely low
- **Time-consuming** to manually track and synthesize

**Next.Epoch solves this** by automating collection, filtering, and summarization.

---

## 3. Target Users

| Persona | Needs |
|---------|-------|
| **AI Researcher** | Track latest papers in their subfield, discover breakthroughs |
| **ML Engineer** | Find new tools, libraries, production-ready techniques |
| **Tech Enthusiast** | Stay informed without reading dense papers |
| **Tech Lead/Manager** | Weekly strategic briefings on AI trends |
| **Content Creator** | Source material for articles, videos, newsletters |

---

## 4. Core Features

### 4.0 MVP Requirements (Clear + Testable)

This section defines **what must exist** for the first usable version. It is written as requirements you can validate with tests, demos, or API calls.

#### In Scope (MVP)
- Ingest from **arXiv** and **GitHub Trending** on a schedule.
- Normalize + deduplicate items into a unified `ContentItem`.
- Produce summaries (cached) and basic scoring (`relevance_score`, `importance_score`, optional `novelty_score`, optional `frontier_score`).
- Provide **REST API** for programmatic access.
- Provide a **Web App UI** for browsing, search, digests, and operational visibility.
- Provide per-field views (top items + momentum) based on stored fields/tags.

#### Out of Scope (MVP)
- User accounts / OAuth.
- Personalized feeds per user.
- CLI as a primary user experience.
- Slack/Discord/Email/WeChat delivery.
- Full automated taxonomy generation (fields can start curated).

#### MVP Functional Requirements
- **FR-1 Ingestion scheduling**: Sources run on configurable intervals; missed runs are retried.
- **FR-2 Idempotency**: Re-running ingestion does not create duplicate content.
- **FR-3 Deduplication**: Near-duplicate items across sources are merged or linked.
- **FR-4 Provenance**: For each item, store when/where it was fetched and how it was parsed.
- **FR-5 Explainability**: For each scored item, expose a short “why this matters” and bounded evidence signals.
- **FR-6 Summaries**: Summary generation is cached and can be re-generated.
- **FR-7 Digests**: API can trigger digest generation asynchronously and poll status.
- **FR-8 Search**: Provide keyword search across title/summary (and raw text when available).
- **FR-9 Observability**: Log ingestion/summarization failures with actionable error messages.
- **FR-10 Cost controls**: Track LLM usage and support per-run cost reporting.
- **FR-11 Web UI**: A browser UI supports the primary user journey end-to-end without requiring API/CLI usage.

### 4.1 Source Tracking

| Source | Type | Priority |
|--------|------|----------|
| **arXiv** | Research papers | P0 (MVP) |
| **GitHub Trending** | Repositories, tools | P0 (MVP) |
| **AI Lab Announcements** (e.g., Anthropic/OpenAI/DeepMind blogs) | Official announcements, research | P1 |
| **AI News Sites** | News articles (The Verge AI, VentureBeat, etc.) | P1 |
| **Twitter/X** | AI researchers, influencers | P2 |

### 4.2 Intelligence Processing

| Feature | Description |
|---------|-------------|
| **Ingestion** | Fetch content from all sources on schedule |
| **Filtering** | Relevance scoring, deduplication, quality check |
| **Categorization** | Auto-tag by topic (LLM, Vision, RL, Safety, etc.) |
| **Summarization** | Generate concise summaries via LLM (LiteLLM proxy) |
| **Trend Detection** | Identify emerging topics and patterns |

### 4.3 Field Tracking Agent

Next.Epoch is not just a feed reader—it is a **frontier-tracking agent** that maintains a continuously-updated view of “what is moving fastest” across AI fields.

#### Definitions
- **Field**: A stable, human-understandable area (e.g., “LLMs”, “Agents”, “Robotics”, “AI Safety”). Fields can have sub-fields.
- **Frontier**: High-impact + high-novelty work with clear momentum. Not necessarily the most popular item; it should be *worth attention now*.

#### Agent Loop (always-on)
1. **Sense**: Fetch new items from sources.
2. **Normalize**: Canonicalize metadata (IDs, URLs, timestamps), extract text.
3. **Dedupe**: Merge near-duplicates across sources.
4. **Enrich**: Tag fields/topics; extract key claims, methods, datasets, code links.
5. **Score**:
       - `relevance_score`: “Is this AI + in-scope?”
       - `importance_score`: “How impactful is it likely to be?”
       - `novelty_score`: “What’s new vs the recent baseline?” (optional)
       - `frontier_score`: Combined ranking score for “frontier” (optional/configurable)
6. **Aggregate**: Compute per-field leaders and momentum.
7. **Explain**: Provide a short, human-readable “why this matters” with evidence.
8. **Deliver**: API/CLI digests + field views.

#### API-Backed Workflows (How the Agent Actually Runs)

This describes the minimum set of API-visible workflows required to operate the agent and debug it.

1) **Scheduled ingestion (primary path)**
- Scheduler triggers ingestion runs per enabled source.
- Operator can inspect run status/history.

**API surface**:
- List sources and their schedules/status.
- Trigger a source refresh manually.
- List and inspect processing runs.

2) **Manual source refresh (operator path)**
- Operator calls “refresh source”.
- System creates an ingestion run and returns a run/job id.
- Operator polls run status until succeeded/failed.

**Acceptance**:
- A refresh returns immediately (async) and does not block on fetching.
- Failures include actionable errors (e.g., rate limit, parse error).

3) **Content browsing + inspection (consumer path)**
- Consumers list/search content.
- Consumers open a content item to see summary + explainability.

**Acceptance**:
- List endpoints are fast and paginated.
- A single item view includes provenance and scoring signals.

4) **On-demand summaries (consumer path)**
- When a paper summary is requested, system returns cached summary if present; otherwise generates and caches.

**Acceptance**:
- Summary endpoint supports multiple styles.
- Summary generation is observable via logs/runs.

5) **Digest generation (consumer/operator path)**
- Consumer triggers digest generation.
- System creates an async digest job/run.
- Consumer polls digest job status and fetches the completed digest.

**Acceptance**:
- Digest generation is idempotent by `(type, period_start, period_end, filters)` or returns the latest equivalent.

6) **Feedback loop (evaluation path)**
- Consumer submits feedback on relevance/value/summary quality.
- System stores feedback for evaluation dashboards and iterative tuning.

**Acceptance**:
- Feedback is attached to a content item and queryable for evaluation.

7) **Reprocess a content item (operator path)**
- Operator triggers a reprocess on a specific content item (e.g., re-summarize with a new prompt, re-score after tuning weights).
- System creates an async run and returns a run id.

**Acceptance**:
- Reprocess does not block and is auditable via `/runs/{id}`.

#### Scoring Signals (MVP)
- **Content signals**: arXiv category, title/abstract keywords, method novelty cues (e.g., “new benchmark”, “state-of-the-art”), presence of code or dataset.
- **Attention signals**: GitHub stars velocity (for repos), cross-source mentions.
- **Recency**: Recent items get a small boost but cannot dominate importance.

### 4.4 Delivery Channels

| Channel | Description | Priority |
|---------|-------------|----------|
| **REST API** | Programmatic access to all data | P0 |
| **Web App** | User-friendly dashboard for browsing + digests | P0 (MVP) |
| **Discord/Slack Bot** | Push notifications to team channels | P1 |
| **Email Newsletter** | Scheduled digest delivery | P1 |
| **CLI Tool** | Terminal-based access for power users | P2 |
| **WeChat MiniProgram** | Mobile access for Chinese users | P2 |
| **Lark (Feishu)** | Enterprise integration | P2 |

### 4.5 Web App UI (MVP)

The MVP must include a **modern, user-friendly web interface** that makes Next.Epoch usable without CLI.

#### Primary UX Goals
- Fast path to “what should I read today?”
- Low friction navigation across fields, time ranges, and item details
- Explainable ranking: show **why** an item is recommended

#### Screens (MVP)
- **Dashboard**: top items (default sort by `frontier_score` if present, else `importance_score`), quick filters (source/type/time), and highlights.
- **Search**: keyword search with filters; paginated results.
- **Item Detail**: full metadata, summary, tags/fields, score breakdown, signals, provenance, original links.
- **Digests**: list digests and view a digest; trigger new digest generation.
- **Runs (Ops)**: view recent runs, run status, and errors (read-only in MVP).
- **Sources (Ops)**: list sources and trigger refresh (optional UI button).
- **Feedback**: submit “relevant/value/summary quality” ratings from item detail.

#### UX Requirements (MVP)
- Responsive layout (desktop first, usable on mobile).
- Loading + error states for all screens.
- Accessibility baseline: keyboard navigation and reasonable contrast.

#### Success Criteria (MVP)
- **Time-to-first-insight**: A new user can find a useful item in < 60 seconds.
- **Performance**: Dashboard and search results load in < 2s p95 on a typical broadband connection.
- **Engagement**: ≥ 30% of weekly active users submit at least one feedback rating.
- **Reliability**: UI gracefully handles empty states and API errors (no blank screens).

#### Authentication (MVP)
- Browser UI uses the existing API-key model. Simplest acceptable MVP: user enters an API key once and it is stored locally (e.g., in browser storage) and sent as `X-API-Key`.

### 4.6 Digest Types

| Type | Frequency | Content |
|------|-----------|---------|
| **Flash** | Real-time | Breaking news, major releases |
| **Daily Digest** | Every 24h | Top papers, news, trending repos |
| **Weekly Briefing** | Every 7d | Comprehensive summary, trends, analysis |
| **Deep Dive** | On-demand | Detailed analysis of specific topic/paper |

### 4.7 Field Views

In addition to digests, the system should support **field-centric views**:
- “Top items in {Field} last 24h/7d”
- “What changed since yesterday?” (new leaders, rising sub-topics)
- “Field momentum” (rising/stable/declining with confidence)

---

## 5. System Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────────┐
│                         SOURCES                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌───────────────┐  │
│  │ arXiv  │ │ News   │ │ GitHub │ │ X/Twitter│ │ Anthropic    │  │
│  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └──────┬────────┘  │
└──────┼──────────┼──────────┼──────────┼─────────────┼───────────┘
       │          │          │          │             │
       ▼          ▼          ▼          ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      INGESTION LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Collectors → Normalizers → Deduplicator → Storage       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE LAYER                            │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐  │
│  │ Categorizer│ │ Summarizer │ │ Ranker     │ │ Trend Detect │  │
│  └────────────┘ └────────────┘ └────────────┘ └──────────────┘  │
│                        │                                         │
│                        ▼                                         │
│              ┌──────────────────┐                               │
│              │ LiteLLM Proxy    │                               │
│              │ (Multi-provider) │                               │
│              └──────────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DELIVERY LAYER                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────┐ │
│  │REST API│ │  CLI   │ │ Bots   │ │ Email  │ │ WeChat/Lark   │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Technical Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **API Framework** | FastAPI |
| **CLI Framework** | Typer / Click |
| **LLM Integration** | LiteLLM (proxy to multiple providers) |
| **Database** | PostgreSQL (primary) + Redis (cache) |
| **Task Queue** | Celery / APScheduler |
| **Containerization** | Docker |
| **Version Control** | Git |

---

## 7. Non-Functional Requirements

### 7.1 Performance
- API response time: < 500ms (p95)
- Digest generation: < 60s for daily digest
- Source refresh: Configurable (default: 1 hour)

### 7.2 Reliability
- 99.5% uptime target
- Graceful degradation if source unavailable
- Retry logic with exponential backoff

### 7.3 Scalability
- Horizontal scaling via containerization
- Async processing for heavy tasks
- Rate limiting per source

### 7.4 Security
- API key authentication
- Rate limiting per user
- No storage of sensitive user data
- HTTPS only

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| **MVP sources active** | arXiv + GitHub |
| **Papers processed/day** | 100+ |
| **Field coverage** | 10+ top-level fields with stable taxonomy |
| **Top-10 relevance** | ≥ 70% “relevant” user rating for top 10 items/day |
| **Top-5 value** | ≥ 60% “worth my time” user rating for top 5/field/week |
| **API latency** | <500ms p95 |
| **Cost control** | Summarization cost per 1k items is tracked and bounded |

---

## 9. Milestones & Phases

### Phase 1: Foundation (MVP)
- [ ] Core ingestion (arXiv + GitHub Trending)
- [ ] Basic summarization
- [ ] REST API
- [ ] Web App UI (Dashboard + Search + Item Detail + Digests)

**MVP Clarification**: ship arXiv-first if needed, but Phase 1 is only “done” when GitHub Trending is also ingested end-to-end.

### Phase 2: Expansion
- [ ] Add remaining sources
- [ ] Discord/Slack integration
- [ ] Email newsletter
- [ ] Trend detection
- [ ] CLI tool

### Phase 3: Scale
- [ ] WeChat MiniProgram
- [ ] Lark integration
- [ ] Advanced personalization
- [ ] Multi-language support

---

## 10. Open Questions

> To be resolved before implementation:

1. **Storage**: SQLite for MVP or jump straight to PostgreSQL?
2. **Hosting**: Self-hosted vs cloud (Vercel, Railway, Fly.io)?
3. **Auth**: Simple API keys vs OAuth for user accounts?
4. **Rate Limits**: What are the rate limits for each source?
5. **Personalization**: Topic filtering per user in MVP?
6. **Taxonomy**: Fixed curated fields vs LLM-generated hierarchical taxonomy? Who can edit?
7. **Frontier scoring**: What’s the initial weight of novelty vs impact vs attention, and how do we validate it?
8. **Evaluation**: What feedback loop exists (explicit ratings, implicit clicks) and what is the success threshold per field?

---

## 11. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **Epoch** | A complete pass through a training dataset; also, an era or period |
| **Digest** | A curated summary of content from a time period |
| **LiteLLM** | Unified interface to multiple LLM providers |

### B. References

- [arXiv API](https://arxiv.org/help/api)
- [LiteLLM Docs](https://docs.litellm.ai/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

*This specification is a living document. Updates will be versioned and tracked in git.*
