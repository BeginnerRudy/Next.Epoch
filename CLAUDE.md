# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Next.Epoch** is an AI frontier intelligence platform—a continuously-running agent that tracks, curates, and summarizes cutting-edge AI research and development. It answers "what should I read today?" by surfacing high-impact, high-novelty content from arXiv, GitHub Trending, and other sources.

## Repository Structure

```
next-epoch/
├── src/next_epoch/          # Python backend
│   ├── api/                 # FastAPI REST API
│   ├── db/                  # SQLAlchemy models & repositories
│   ├── ingestion/           # Source collectors & normalizers
│   ├── intelligence/        # Scoring & summarization
│   ├── schemas/             # Pydantic models
│   └── tasks/               # Background job scheduling
├── web/                     # Next.js frontend
│   └── src/
│       ├── app/             # Pages (Dashboard, Search, Content, Digests)
│       ├── components/      # React components
│       └── lib/             # API client & utilities
├── tests/                   # Test suite (104 tests)
├── alembic/                 # Database migrations
├── specs/                   # Specifications
│   ├── SPEC.md             # Product spec
│   ├── MODELS.md           # Data models
│   └── openapi.yaml        # API spec
└── IMPLEMENTATION_PLAN.md   # Development stages (MVP complete)
```

## Running the Application

### Backend (Python/FastAPI)

```bash
# Install dependencies
pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env with DATABASE_URL and LLM API keys

# Run database migrations
alembic upgrade head

# Start API server
uvicorn next_epoch.api.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend (Next.js)

```bash
cd web
npm install
npm run dev
# UI available at http://localhost:3000
```

### Running Tests

```bash
pytest                    # All tests
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests only
pytest --cov=next_epoch   # With coverage
```

## Technical Stack

| Layer | Technology |
|-------|------------|
| Backend API | Python 3.11+, FastAPI, Pydantic 2.x |
| Database | PostgreSQL, SQLAlchemy 2.0 (async), Alembic |
| LLM Integration | LiteLLM (OpenAI, Anthropic, etc.) |
| Scheduling | APScheduler |
| Frontend | Next.js 14, TypeScript, Tailwind CSS, React Query |

## Architecture

Three-layer design:
1. **Ingestion**: Collectors → Normalizers → Storage
2. **Intelligence**: Relevance Scorer, Importance Scorer, Summarizer (via LiteLLM)
3. **Delivery**: REST API, Next.js Web App

### Scoring Algorithm

Hybrid approach: rule-based for relevance, LLM-assisted for importance.

| Score | Weight | Method |
|-------|--------|--------|
| `relevance` | 20% | Rule-based (category_match + keyword_density) |
| `importance` | 50% | Hybrid (author_authority + has_code + stars_velocity) |
| `novelty` | 20% | LLM-assisted (vs recent baseline) |
| `recency` | 10% | Time decay boost |

**Frontier Score** = 0.2×relevance + 0.5×importance + 0.2×novelty + 0.1×recency

Key signals: `category_match`, `author_authority`, `has_code`, `stars_velocity`, `keyword_density`

## Key Files

### Backend
- `src/next_epoch/api/main.py` - FastAPI application entry point
- `src/next_epoch/config.py` - Environment configuration
- `src/next_epoch/db/models.py` - SQLAlchemy database models
- `src/next_epoch/intelligence/scorer.py` - Frontier score calculation
- `src/next_epoch/ingestion/collectors/` - arXiv and GitHub collectors
- `src/next_epoch/tasks/scheduler.py` - Background job scheduling

### Frontend
- `web/src/app/page.tsx` - Dashboard page
- `web/src/app/search/page.tsx` - Search page
- `web/src/app/content/[id]/page.tsx` - Content detail page
- `web/src/lib/api.ts` - API client

## Common Tasks

### Add a new source collector
1. Create `src/next_epoch/ingestion/collectors/newsource.py`
2. Extend `BaseCollector` class
3. Implement `collect()` method returning raw items
4. Add normalizer logic in `normalizers/content.py`

### Add a new API endpoint
1. Create route in `src/next_epoch/api/routes/`
2. Register router in `src/next_epoch/api/main.py`
3. Add tests in `tests/integration/test_api.py`

### Add a new scoring signal
1. Add signal function in `src/next_epoch/intelligence/importance.py` or `relevance.py`
2. Include in score calculation
3. Add to `signals` list in result

## Development Guidelines

### Philosophy
- Incremental progress over big bangs
- Clear intent over clever code—be boring and obvious
- Avoid premature abstractions

### Process
1. **Understand**: Study existing patterns before implementing
2. **Test**: Write test first (TDD: red → green → refactor)
3. **Commit**: Must compile, pass tests, explain "why"

### Technical Standards
- Composition over inheritance
- Explicit data flow, fail fast with descriptive errors
- Never disable tests—fix them
- All IDs use UUIDv7

### Definition of Done
- Tests passing (104 tests in suite)
- Code follows existing conventions
- Commit messages are clear

## MVP Status: Complete ✅

All MVP features implemented:
- [x] arXiv + GitHub Trending ingestion
- [x] Scoring algorithm with explainability
- [x] REST API with all endpoints
- [x] Next.js web dashboard
- [x] Search with filters
- [x] Content detail with score breakdown
- [x] Digests (daily/weekly)
- [x] 104 tests passing

## Docker Deployment (China Network)

### Quick Start
```bash
docker compose up -d
```

### Services
| Service | URL | Description |
|---------|-----|-------------|
| Web Dashboard | http://localhost:3000 | Next.js frontend |
| API Docs | http://localhost:8000/docs | Swagger/OpenAPI |
| API | http://localhost:8000/api/v1 | REST API |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |

### China Network Configuration
The Dockerfiles are configured with China mirrors:
- **Debian packages**: Aliyun mirror (`mirrors.aliyun.com`)
- **PyPI**: Tsinghua mirror (`pypi.tuna.tsinghua.edu.cn`)
- **Alpine packages**: Aliyun mirror
- **Docker Hub**: Configured in `~/.docker/daemon.json`

### Environment Variables
All config uses `NEXT_EPOCH_` prefix (set in docker-compose.yaml):
- `NEXT_EPOCH_DATABASE_URL` - PostgreSQL connection (async)
- `NEXT_EPOCH_DATABASE_URL_SYNC` - PostgreSQL connection (sync, for migrations)
- `NEXT_EPOCH_REDIS_URL` - Redis connection
- `NEXT_EPOCH_LLM_API_KEY` - OpenAI/Anthropic API key

### Useful Commands
```bash
# Trigger GitHub ingestion manually
curl -X POST http://localhost:8000/api/v1/sources/github/refresh

# Trigger arXiv ingestion (requires VPN in China)
curl -X POST http://localhost:8000/api/v1/sources/arxiv/refresh

# View ingestion runs
curl http://localhost:8000/api/v1/runs

# Check content count
curl http://localhost:8000/api/v1/content
```

## Current Progress (Jan 2026)

### Working
- ✅ Docker Compose deployment with China mirrors
- ✅ GitHub Trending ingestion (auto-runs every 60 minutes)
- ✅ Scoring and ranking algorithm
- ✅ REST API with all endpoints
- ✅ Web dashboard showing real data

### Known Issues / Next Steps
1. **arXiv ingestion blocked in China** - Need to add HTTP proxy support to arXiv collector for China users
2. **Docker mirror timeouts** - Intermittent issues with China Docker Hub mirrors; retry usually works
3. **Web Dockerfile rebuild** - May fail due to Alpine mirror issues; use cached image when possible

### To Enable arXiv in China
Add proxy support to `src/next_epoch/ingestion/collectors/arxiv.py`:
```python
# Pass proxy to httpx client
proxy = os.getenv("NEXT_EPOCH_HTTP_PROXY")
if proxy:
    self.client = httpx.AsyncClient(proxy=proxy, ...)
```
Then set `NEXT_EPOCH_HTTP_PROXY=http://host.docker.internal:7897` in docker-compose.yaml.
