<div align="center">

# ⚡ Next.Epoch

### AI Frontier Intelligence Platform

*Track the cutting edge of AI research and development*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API](#-api) • [Contributing](#-contributing)

---

<img src="https://via.placeholder.com/800x400/0ea5e9/ffffff?text=Next.Epoch+Dashboard" alt="Next.Epoch Dashboard" width="800"/>

</div>

## 🎯 What is Next.Epoch?

**Next.Epoch** is your AI research assistant that answers the question: *"What should I read today?"*

It continuously monitors the AI frontier—arXiv papers, GitHub trending repositories, and more—to surface high-impact, high-novelty content. No more FOMO. No more endless scrolling. Just the insights that matter.

### The Problem

The AI field moves at breakneck speed. Hundreds of papers drop daily. Repositories go viral overnight. Keeping up is a full-time job.

### The Solution

Next.Epoch acts as your intelligent filter:

- 🔍 **Ingests** content from multiple sources (arXiv, GitHub Trending)
- 🧠 **Scores** each item using hybrid rule-based + LLM analysis
- 📊 **Ranks** by a unified "Frontier Score" combining relevance, importance, and novelty
- 📝 **Summarizes** key findings with AI-generated explanations
- 📬 **Delivers** personalized digests so you never miss what matters

---

## ✨ Features

### 📡 Multi-Source Ingestion
- **arXiv** — Latest AI/ML papers from cs.AI, cs.LG, cs.CL
- **GitHub Trending** — Hot repositories in machine learning
- *Coming soon: Hacker News, Twitter/X, RSS feeds*

### 🎯 Intelligent Scoring

Every piece of content gets a **Frontier Score** (0-100) based on:

| Component | Weight | Method |
|-----------|--------|--------|
| **Relevance** | 20% | Rule-based (keywords, categories) |
| **Importance** | 50% | Hybrid (author authority, code availability, stars) |
| **Novelty** | 20% | LLM-assisted (vs recent baseline) |
| **Recency** | 10% | Time decay boost |

### 🔬 Explainable Rankings

No black boxes. Every score comes with evidence signals:

```
Score: 92/100 (High Impact)
├── category_match: cs.AI, cs.LG ✓
├── author_authority: OpenAI, DeepMind ✓
├── has_code: true ✓
├── keyword_density: 85%
└── citation_potential: High
```

### 📰 AI-Generated Digests

Daily and weekly summaries organized by:
- Top papers of the day
- Trending repositories
- Emerging themes
- Field-specific highlights

### 🖥️ Modern Web Interface

Beautiful, responsive dashboard built with Next.js:
- Real-time content feed
- Advanced search with filters
- Detailed item views with score breakdowns
- Digest browsing and reading

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/next-epoch.git
cd next-epoch

# Backend
pip install -e ".[dev]"

# Frontend
cd web && npm install && cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/next_epoch

# LLM Provider (via LiteLLM)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# Optional
REDIS_URL=redis://localhost:6379
```

### 3. Initialize Database

```bash
alembic upgrade head
```

### 4. Run

```bash
# Terminal 1: Backend API
uvicorn next_epoch.api.main:app --reload

# Terminal 2: Frontend
cd web && npm run dev
```

🎉 Open http://localhost:3000 and explore!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INGESTION LAYER                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  arXiv Client   │  GitHub Scraper │  ... more collectors        │
└────────┬────────┴────────┬────────┴─────────────────────────────┘
         │                 │
         ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NORMALIZER + DEDUPER                       │
│              Unified ContentItem → canonical_ref                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      INTELLIGENCE LAYER                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│ Relevance Score │ Importance Score│ Summarizer (LLM)            │
│   (Rule-based)  │ (Hybrid + LLM)  │                             │
└────────┬────────┴────────┬────────┴─────────────────────────────┘
         │                 │
         ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTIER SCORE + RANKING                     │
│         0.2×rel + 0.5×imp + 0.2×nov + 0.1×recency              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DELIVERY LAYER                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│    REST API     │    Web App      │  Digests (Daily/Weekly)     │
│   (FastAPI)     │   (Next.js)     │                             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **API** | FastAPI, Pydantic, async/await |
| **Database** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **LLM** | LiteLLM (OpenAI, Anthropic, etc.) |
| **Scheduling** | APScheduler |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **State** | React Query |

---

## 📡 API

### Core Endpoints

```
GET  /api/v1/health              # Health check
GET  /api/v1/content             # List content (paginated)
GET  /api/v1/content/{id}        # Get content detail
GET  /api/v1/content/search      # Search content
GET  /api/v1/digests             # List digests
GET  /api/v1/digests/latest      # Get latest digest
GET  /api/v1/sources             # List sources
POST /api/v1/sources/{id}/refresh # Trigger source refresh
GET  /api/v1/fields              # List taxonomy fields
GET  /api/v1/runs                # List processing runs
```

### Example: Get Top Content

```bash
curl "http://localhost:8000/api/v1/content?per_page=5" | jq
```

```json
{
  "data": [
    {
      "id": "01234567-89ab-cdef-0123-456789abcdef",
      "title": "Attention Is All You Need: Revisited",
      "type": "paper",
      "source": "arxiv",
      "frontier_score": 0.92,
      "score_breakdown": {
        "relevance": 0.95,
        "importance": 0.88,
        "novelty": 0.85,
        "signals": [...]
      }
    }
  ],
  "pagination": { "page": 1, "total": 150 }
}
```

Full API documentation at http://localhost:8000/docs

---

## 📁 Project Structure

```
next-epoch/
├── 📄 pyproject.toml          # Python package config
├── 📄 alembic.ini             # Database migrations config
├── 📁 alembic/                # Migration scripts
├── 📁 specs/                  # Specifications
│   ├── SPEC.md               # Product spec
│   ├── MODELS.md             # Data models
│   └── openapi.yaml          # API spec
├── 📁 src/next_epoch/         # Python source
│   ├── 📁 api/               # FastAPI application
│   ├── 📁 db/                # Database layer
│   ├── 📁 ingestion/         # Source collectors
│   ├── 📁 intelligence/      # Scoring & summarization
│   ├── 📁 schemas/           # Pydantic models
│   └── 📁 tasks/             # Background jobs
├── 📁 tests/                  # Test suite
│   ├── 📁 unit/
│   └── 📁 integration/
└── 📁 web/                    # Next.js frontend
    ├── 📁 src/app/           # Pages
    ├── 📁 src/components/    # React components
    └── 📁 src/lib/           # Utilities
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=next_epoch --cov-report=html

# Just unit tests
pytest tests/unit/

# Just integration tests
pytest tests/integration/
```

**Current Coverage:** 104 tests passing ✅

---

## 🛣️ Roadmap

### MVP (Complete ✅)
- [x] arXiv + GitHub ingestion
- [x] Scoring algorithm
- [x] REST API
- [x] Web dashboard
- [x] Daily digests

### Phase 2 (Planned)
- [ ] Hacker News collector
- [ ] Twitter/X integration
- [ ] Novelty scoring with embeddings
- [ ] User accounts & preferences
- [ ] Personalized recommendations

### Phase 3 (Future)
- [ ] Slack/Discord notifications
- [ ] Email digests
- [ ] RSS feed output
- [ ] Browser extension
- [ ] Mobile app

---

## 🤝 Contributing

Contributions are welcome! Please read our guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit with clear messages
6. Open a Pull Request

### Development Philosophy

- **Incremental progress** over big bangs
- **Clear intent** over clever code
- **Test-driven development** (red → green → refactor)
- **Composition over inheritance**

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for the AI research community**

[Report Bug](https://github.com/yourusername/next-epoch/issues) · [Request Feature](https://github.com/yourusername/next-epoch/issues)

</div>
