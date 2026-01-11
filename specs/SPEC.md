# Next.Epoch - Product Specification

> **Version:** 0.1.0
> **Status:** Draft
> **Last Updated:** 2025-01-11

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

### 4.1 Source Tracking

| Source | Type | Priority |
|--------|------|----------|
| **arXiv** | Research papers | P0 (Must have) |
| **AI News Sites** | News articles (The Verge AI, VentureBeat, etc.) | P0 |
| **GitHub Trending** | Repositories, tools | P1 |
| **Twitter/X** | AI researchers, influencers | P1 |
| **Anthropic Website** | Official announcements, research | P0 |

### 4.2 Intelligence Processing

| Feature | Description |
|---------|-------------|
| **Ingestion** | Fetch content from all sources on schedule |
| **Filtering** | Relevance scoring, deduplication, quality check |
| **Categorization** | Auto-tag by topic (LLM, Vision, RL, Safety, etc.) |
| **Summarization** | Generate concise summaries via LLM (LiteLLM proxy) |
| **Trend Detection** | Identify emerging topics and patterns |

### 4.3 Delivery Channels

| Channel | Description | Priority |
|---------|-------------|----------|
| **REST API** | Programmatic access to all data | P0 |
| **CLI Tool** | Terminal-based access for power users | P0 |
| **Discord/Slack Bot** | Push notifications to team channels | P1 |
| **Email Newsletter** | Scheduled digest delivery | P1 |
| **WeChat MiniProgram** | Mobile access for Chinese users | P2 |
| **Lark (Feishu)** | Enterprise integration | P2 |

### 4.4 Digest Types

| Type | Frequency | Content |
|------|-----------|---------|
| **Flash** | Real-time | Breaking news, major releases |
| **Daily Digest** | Every 24h | Top papers, news, trending repos |
| **Weekly Briefing** | Every 7d | Comprehensive summary, trends, analysis |
| **Deep Dive** | On-demand | Detailed analysis of specific topic/paper |

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
| **Sources tracked** | 5+ active sources |
| **Papers processed/day** | 100+ |
| **Digest accuracy** | >90% relevance rating |
| **API latency** | <500ms p95 |
| **User satisfaction** | >4.0/5.0 rating |

---

## 9. Milestones & Phases

### Phase 1: Foundation (MVP)
- [ ] Core ingestion (arXiv only)
- [ ] Basic summarization
- [ ] REST API
- [ ] CLI tool

### Phase 2: Expansion
- [ ] Add remaining sources
- [ ] Discord/Slack integration
- [ ] Email newsletter
- [ ] Trend detection

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
