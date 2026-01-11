# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Next.Epoch** is an AI frontier intelligence platform—a continuously-running agent that tracks, curates, and summarizes cutting-edge AI research and development. It answers "what should I read today?" by surfacing high-impact, high-novelty content from arXiv, GitHub Trending, and other sources.

## Repository Structure

- `specs/SPEC.md` - Product specification (MVP requirements, features, architecture)
- `specs/MODELS.md` - Data models (entities, relationships, enums)
- `specs/openapi.yaml` - REST API specification (OpenAPI 3.1)
- `specs/DevelopmentGuidelines.md` - Development philosophy and process

## Technical Stack

Python 3.11+, FastAPI, Typer/Click, LiteLLM, PostgreSQL + Redis, Celery/APScheduler, Docker

## Architecture

Three-layer design:
1. **Ingestion**: Collectors → Normalizers → Deduplicator → Storage
2. **Intelligence**: Categorizer, Summarizer, Ranker, Trend Detection (via LiteLLM)
3. **Delivery**: REST API, Web App, Discord/Slack, Email

### Agent Loop (Field Tracking)
Sense → Normalize → Dedupe → Enrich → Score → Aggregate → Explain → Deliver

### Scoring Algorithm

Hybrid approach: rule-based for relevance, LLM-assisted for importance.

| Score | Method | Formula |
|-------|--------|---------|
| `relevance` | Rules | category_match + keyword_density + source_relevance |
| `importance` | Hybrid | 0.5 * rules + 0.5 * LLM judgment |
| `novelty` | LLM | vs recent baseline (optional, deferred for MVP) |
| `frontier` | Combined | 0.2*rel + 0.5*imp + 0.2*nov + 0.1*recency |

Key signals: `category_match`, `author_authority`, `has_code`, `stars_velocity`, `cross_mentions`

See `specs/SPEC.md` section "Scoring Algorithm" for full details.

## MVP Scope

**In scope**: arXiv + GitHub Trending ingestion, summaries, REST API, Web App UI
**Out of scope**: User accounts, personalized feeds, CLI as primary UX, Slack/Discord/Email

### Key Functional Requirements
- FR-1: Scheduled ingestion with retry
- FR-2: Idempotent ingestion (no duplicates on re-run)
- FR-3: Near-duplicate deduplication across sources
- FR-5: Explainability ("why this matters" + evidence signals)
- FR-9: Observability (log failures with actionable errors)
- FR-10: Cost controls (track LLM usage per run)

## Key Data Models

- **ContentItem**: Unified wrapper with scores, signals, provenance, field mappings
- **Field**: Taxonomy entry (e.g., "agents", "llm", "robotics") with hierarchy
- **ProcessingRun**: Auditable run record (ingest/enrich/summarize/score/digest)
- **Feedback**: User ratings for evaluation loop

All IDs use UUIDv7. All content has `canonical_ref` for deduplication.

## Development Guidelines

### Philosophy
- Incremental progress over big bangs
- Clear intent over clever code—be boring and obvious
- Avoid premature abstractions

### Process
1. **Plan**: Break complex work into 3-5 stages in `IMPLEMENTATION_PLAN.md`
2. **Understand**: Study existing patterns before implementing
3. **Test**: Write test first (TDD: red → green → refactor)
4. **Commit**: Must compile, pass tests, explain "why"

### When Stuck (After 3 Attempts)
STOP. Document failures, research alternatives, question fundamentals.

### Technical Standards
- Composition over inheritance
- Explicit data flow, fail fast with descriptive errors
- Never disable tests—fix them
- No `--no-verify` to bypass hooks

### Decision Framework
1. Testability → 2. Readability → 3. Consistency → 4. Simplicity → 5. Reversibility

### Definition of Done
- Tests passing, code follows conventions, no linter warnings
- Commit messages are clear, no TODOs without issue numbers
