# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Next.Epoch** is an AI frontier intelligence platform that tracks, curates, and summarizes cutting-edge AI research and development from sources like arXiv, GitHub, Twitter, and AI news sites. Currently in the specification phase.

## Repository Structure

- `specs/SPEC.md` - Product specification (vision, features, architecture)
- `specs/MODELS.md` - Data models specification (entities, relationships, validation)
- `specs/openapi.yaml` - REST API specification (OpenAPI 3.1)
- `specs/DevelopmentGuidelines.md` - Development philosophy and process

## Technical Stack

Python 3.11+, FastAPI, Typer/Click (CLI), LiteLLM, PostgreSQL + Redis, Celery/APScheduler, Docker

## Architecture

Three-layer design:
1. **Ingestion**: Collectors → Normalizers → Deduplicator → Storage
2. **Intelligence**: Categorizer, Summarizer, Ranker, Trend Detection (via LiteLLM proxy)
3. **Delivery**: REST API, CLI, Discord/Slack, Email, WeChat/Lark

## Development Guidelines

### Philosophy
- Incremental progress over big bangs - small changes that compile and pass tests
- Clear intent over clever code - be boring and obvious
- Avoid premature abstractions - choose the simplest solution

### Process
1. **Plan**: Break complex work into 3-5 stages, document in `IMPLEMENTATION_PLAN.md`
2. **Understand**: Study existing patterns before implementing
3. **Test**: Write test first (TDD: red → green → refactor)
4. **Commit**: Clear message explaining "why", must compile and pass all tests

### When Stuck (After 3 Attempts) - STOP and:
- Document what failed (attempts, errors, reasons)
- Research 2-3 alternative approaches
- Question fundamentals: right abstraction? can it be split? simpler approach?

### Technical Standards
- Composition over inheritance, interfaces over singletons
- Explicit data flow, fail fast with descriptive errors
- Never disable tests - fix them
- No `--no-verify` to bypass hooks

### Decision Framework (in priority order)
1. Testability
2. Readability
3. Consistency with project patterns
4. Simplicity
5. Reversibility

### Definition of Done
- Tests written and passing
- Code follows project conventions
- No linter/formatter warnings
- Commit messages are clear
- No TODOs without issue numbers
