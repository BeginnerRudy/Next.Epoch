# Next.Epoch - Implementation Plan

> **Version:** 1.1.0
> **Created:** 2026-01-11
> **Updated:** 2026-01-11
> **Target:** MVP (Phase 1) ✅ COMPLETE

---

## Overview

This plan breaks down the MVP implementation into stages, each delivering working, tested code.

**MVP Scope:**
- arXiv + GitHub Trending ingestion ✅
- Normalize + deduplicate items into unified `ContentItem` ✅
- Summaries (cached) and basic scoring ✅
- REST API ✅
- Web App UI (Dashboard, Search, Item Detail, Digests) - Deferred to post-MVP

---

## Stage 1: Project Foundation ✅

**Goal**: Establish project structure, dependencies, and core domain models.

**Success Criteria**:
- [x] Python package structure with proper `pyproject.toml`
- [x] Core Pydantic schemas matching MODELS.md
- [x] Configuration management (env-based)
- [x] Linting/formatting setup (ruff, black)
- [x] Basic test infrastructure

**Deliverables**:
- `pyproject.toml` with all MVP dependencies
- `src/next_epoch/` package structure
- `src/next_epoch/schemas/` - all Pydantic models
- `src/next_epoch/config.py` - configuration
- `tests/` - test infrastructure

**Status**: ✅ Complete

---

## Stage 2: Database Layer ✅

**Goal**: Implement database models and repository pattern for persistence.

**Success Criteria**:
- [x] SQLAlchemy models for all entities
- [x] Repository pattern for CRUD operations
- [x] Connection pooling and session management

**Deliverables**:
- `src/next_epoch/db/models.py` - SQLAlchemy models
- `src/next_epoch/db/repositories/` - repository classes
- `src/next_epoch/db/session.py` - session management

**Status**: ✅ Complete

---

## Stage 3: Ingestion Layer ✅

**Goal**: Implement collectors for arXiv and GitHub Trending.

**Success Criteria**:
- [x] arXiv API client fetching cs.AI, cs.LG, cs.CL papers
- [x] GitHub Trending scraper for AI-related repos
- [x] Normalizers producing unified ContentItem
- [x] Provenance tracking

**Deliverables**:
- `src/next_epoch/ingestion/collectors/arxiv.py`
- `src/next_epoch/ingestion/collectors/github.py`
- `src/next_epoch/ingestion/normalizers/content.py`

**Status**: ✅ Complete

---

## Stage 4: REST API ✅

**Goal**: Implement FastAPI endpoints per openapi.yaml spec.

**Success Criteria**:
- [x] All content endpoints (list, get, search, feedback)
- [x] All digest endpoints
- [x] All source endpoints
- [x] All runs endpoints
- [x] All fields endpoints
- [x] Health endpoints
- [x] API key authentication
- [x] Proper error responses

**Deliverables**:
- `src/next_epoch/api/main.py` - FastAPI app
- `src/next_epoch/api/routes/` - route modules
- `src/next_epoch/api/deps.py` - dependencies

**Status**: ✅ Complete

---

## Stage 5: Intelligence Layer ✅

**Goal**: Implement scoring, summarization, and LLM integration.

**Success Criteria**:
- [x] Relevance scoring (rule-based)
- [x] Importance scoring (hybrid: rules + LLM)
- [x] Summary generation via LiteLLM
- [x] Cost tracking per run
- [x] Explainability (score breakdown + signals)

**Deliverables**:
- `src/next_epoch/intelligence/scorer.py` - combined scorer with frontier score
- `src/next_epoch/intelligence/relevance.py` - rule-based relevance scoring
- `src/next_epoch/intelligence/importance.py` - hybrid importance scoring
- `src/next_epoch/intelligence/summarizer.py` - LLM summarization
- `src/next_epoch/intelligence/llm_client.py` - LiteLLM wrapper with cost tracking

**Status**: ✅ Complete

---

## Stage 6: Background Tasks & Scheduling ✅

**Goal**: Implement scheduled ingestion and async processing.

**Success Criteria**:
- [x] APScheduler for scheduled ingestion
- [x] Background task queue for async operations
- [x] Processing run tracking
- [x] Retry logic with exponential backoff

**Deliverables**:
- `src/next_epoch/tasks/scheduler.py` - APScheduler setup
- `src/next_epoch/tasks/ingestion.py` - IngestionService

**Status**: ✅ Complete

---

## Stage 7: Alembic Migrations ✅

**Goal**: Set up database migrations.

**Success Criteria**:
- [x] Alembic initialization
- [x] Migration template
- [x] Environment configuration

**Deliverables**:
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Migration environment
- `alembic/script.py.mako` - Migration template

**Status**: ✅ Complete

---

## Stage 8: Testing ✅

**Goal**: Comprehensive test coverage.

**Success Criteria**:
- [x] Unit tests for schemas
- [x] Unit tests for config
- [x] Unit tests for collectors
- [x] Unit tests for normalizers
- [x] Unit tests for scoring
- [x] API integration tests

**Deliverables**:
- `tests/unit/test_schemas.py`
- `tests/unit/test_config.py`
- `tests/unit/test_collectors.py`
- `tests/unit/test_normalizers.py`
- `tests/unit/test_scoring.py`
- `tests/integration/test_api.py`

**Status**: ✅ Complete (104 tests passing)

---

## Stage 9: Web UI (Post-MVP)

**Goal**: Implement basic web interface.

**Success Criteria**:
- [ ] Dashboard with top items
- [ ] Search page
- [ ] Item detail view
- [ ] Digest list and view

**Note**: Web UI deferred to post-MVP; backend takes priority.

**Status**: Not Started

---

## Test Summary

**Total Tests**: 104 passing
- Schema tests: 25
- Config tests: 7
- Collector tests: 14
- Normalizer tests: 7
- Scoring tests: 20
- API integration tests: 21
- Additional tests: 10

---

## MVP Complete! 🎉

All backend stages are complete. The MVP includes:

### Working Features:
1. **Ingestion Pipeline**
   - arXiv collector for AI research papers
   - GitHub Trending collector for repositories
   - Content normalizers producing unified ContentItem

2. **Intelligence Layer**
   - Rule-based relevance scoring (keyword density, category match)
   - Hybrid importance scoring (author authority, code detection, stars velocity)
   - LLM-powered summarization via LiteLLM
   - Frontier score calculation with recency boost

3. **REST API**
   - Content endpoints (list, get, search)
   - Digest endpoints
   - Source endpoints with refresh triggers
   - Processing run endpoints
   - Fields/taxonomy endpoints
   - Health endpoints

4. **Background Tasks**
   - APScheduler for scheduled ingestion (every 2 hours)
   - Ingestion service orchestrating full pipeline

5. **Database**
   - SQLAlchemy 2.0 async models
   - Repository pattern for data access
   - Alembic migrations setup

---

## Next Steps (Post-MVP)

1. **Deploy to production**
   - Set up PostgreSQL and Redis
   - Configure LLM API keys
   - Run Alembic migrations
   - Start API server with uvicorn

2. **Web UI**
   - Dashboard showing top items by frontier score
   - Search with filters
   - Item detail with explanation
   - Digest viewing

3. **Enhancements**
   - Add novelty scoring (vs recent baseline)
   - Implement deduplication service
   - Add Discord/Slack notifications
   - Add user accounts and personalized feeds

---

## Project Structure (Final)

```
next-epoch/
├── pyproject.toml          # Package config with all dependencies
├── alembic.ini             # Alembic configuration
├── .env.example            # Environment variables template
├── .gitignore
├── CLAUDE.md               # AI assistant instructions
├── IMPLEMENTATION_PLAN.md  # This file
├── alembic/                # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── specs/                  # Specifications
│   ├── SPEC.md            # Product spec
│   ├── MODELS.md          # Data models
│   ├── openapi.yaml       # API spec
│   └── DevelopmentGuidelines.md
├── src/next_epoch/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── schemas/            # Pydantic models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── enums.py
│   │   ├── content.py
│   │   ├── field.py
│   │   ├── digest.py
│   │   ├── run.py
│   │   ├── source.py
│   │   ├── feedback.py
│   │   └── pagination.py
│   ├── db/                 # Database layer
│   │   ├── __init__.py
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── session.py      # Session management
│   │   └── repositories/   # Repository pattern
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── content.py
│   │       ├── paper.py
│   │       ├── repository.py
│   │       └── run.py
│   ├── ingestion/          # Ingestion layer
│   │   ├── __init__.py
│   │   ├── collectors/     # Source collectors
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── arxiv.py
│   │   │   └── github.py
│   │   └── normalizers/    # Content normalizers
│   │       ├── __init__.py
│   │       └── content.py
│   ├── intelligence/       # Intelligence layer
│   │   ├── __init__.py
│   │   ├── relevance.py    # Relevance scoring
│   │   ├── importance.py   # Importance scoring
│   │   ├── scorer.py       # Combined scorer
│   │   ├── llm_client.py   # LiteLLM wrapper
│   │   └── summarizer.py   # Content summarization
│   ├── tasks/              # Background tasks
│   │   ├── __init__.py
│   │   ├── scheduler.py    # APScheduler setup
│   │   └── ingestion.py    # Ingestion service
│   └── api/                # REST API
│       ├── __init__.py
│       ├── main.py         # FastAPI app
│       ├── deps.py         # Dependencies
│       └── routes/         # Endpoint modules
│           ├── __init__.py
│           ├── content.py
│           ├── digests.py
│           ├── sources.py
│           ├── runs.py
│           ├── fields.py
│           └── health.py
└── tests/
    ├── conftest.py         # Test fixtures
    ├── unit/               # Unit tests
    │   ├── test_schemas.py
    │   ├── test_config.py
    │   ├── test_collectors.py
    │   ├── test_normalizers.py
    │   └── test_scoring.py
    └── integration/        # Integration tests
        └── test_api.py
```
