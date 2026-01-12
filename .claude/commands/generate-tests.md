---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [file-path] | [module-name]
description: Generate comprehensive pytest test suite with unit, integration, and edge case coverage
---

# Generate Tests

Generate comprehensive pytest test suite for: $ARGUMENTS

## Current Testing Setup

- Test framework: pytest with pytest-asyncio
- Configuration: @pyproject.toml (see [tool.pytest.ini_options])
- Existing tests: !`find tests -name "test_*.py" | head -10`
- Fixtures: @tests/conftest.py
- Target file: @$ARGUMENTS (if file path provided)

## Task

I'll analyze the target code and create complete test coverage including:

1. Unit tests for individual functions and classes
2. Integration tests for component interactions
3. Edge case and error handling tests
4. Mock implementations for external dependencies (httpx, LLM, database)
5. Async test support with pytest-asyncio
6. Factory fixtures for test data generation

## Process

I'll follow these steps:

1. Analyze the target file/module structure
2. Identify all testable functions, methods, and behaviors
3. Examine existing test patterns in `tests/`
4. Create test files following project naming conventions (`test_*.py`)
5. Implement comprehensive test cases with proper fixtures
6. Add necessary mocks using pytest-mock and respx
7. Verify test coverage and add missing test cases

## Test Types

### Unit Tests

- Individual function testing with various inputs
- Pydantic model validation testing
- Schema serialization/deserialization
- Utility function edge cases

### Integration Tests

- FastAPI endpoint testing with TestClient
- Database repository operations
- API integration with mocked responses
- Service layer integration

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Testing Best Practices

### Test Structure

- Use descriptive test names: `test_<function>_<scenario>_<expected>`
- Follow AAA pattern (Arrange, Act, Assert)
- Group related tests with classes: `class TestCollectorName:`
- Use fixtures from `conftest.py` for shared setup

### Mocking Strategy

- Use `pytest-mock` for general mocking
- Use `respx` for mocking httpx requests
- Mock LiteLLM/LLM calls to avoid API costs
- Use `factory-boy` and `faker` for test data

### Project Conventions

- Test files: `tests/unit/test_<module>.py` or `tests/integration/test_<feature>.py`
- Fixtures: Add shared fixtures to `tests/conftest.py`
- Async: Use `@pytest.mark.asyncio` decorator
- Coverage: Aim for 80%+ on critical paths

### Example Test Pattern

```python
"""Tests for the scoring module."""

import pytest
from unittest.mock import AsyncMock, patch

from next_epoch.intelligence.scorer import RelevanceScorer


class TestRelevanceScorer:
    """Tests for RelevanceScorer."""

    @pytest.fixture
    def scorer(self):
        """Create a scorer instance."""
        return RelevanceScorer()

    def test_score_paper_with_ai_keywords_returns_high_score(self, scorer):
        """Papers with AI keywords should have high relevance."""
        paper = {"title": "Transformer Architecture for NLP", "abstract": "..."}
        score = scorer.score(paper)
        assert score >= 0.7

    def test_score_paper_without_ai_keywords_returns_low_score(self, scorer):
        """Papers without AI keywords should have low relevance."""
        paper = {"title": "Cooking Recipes", "abstract": "..."}
        score = scorer.score(paper)
        assert score < 0.3

    @pytest.mark.asyncio
    async def test_async_batch_scoring(self, scorer):
        """Batch scoring should process all items."""
        papers = [{"title": f"Paper {i}"} for i in range(10)]
        scores = await scorer.batch_score(papers)
        assert len(scores) == 10
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_<module>.py

# Run with coverage
pytest --cov=src/next_epoch --cov-report=term-missing

# Run tests matching pattern
pytest -k "test_scoring"

# Run with verbose output
pytest -v --tb=short
```

I'll create tests that follow this project's patterns and integrate with existing fixtures.
