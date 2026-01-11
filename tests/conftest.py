"""Test configuration and fixtures."""

import pytest
from datetime import datetime


@pytest.fixture
def sample_paper_data():
    """Sample paper data for testing."""
    return {
        "external_id": "2401.12345",
        "canonical_ref": "arxiv:2401.12345",
        "title": "Test Paper: A Novel Approach to AI Testing",
        "authors": [
            {"name": "John Doe", "affiliation": "Test University"},
            {"name": "Jane Smith", "affiliation": "AI Research Lab"},
        ],
        "abstract": "This is a test abstract about machine learning and transformers.",
        "url": "https://arxiv.org/abs/2401.12345",
        "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf",
        "published_at": datetime(2024, 1, 15, 12, 0, 0),
        "categories": ["cs.AI", "cs.LG"],
        "tags": ["machine-learning", "transformers"],
    }


@pytest.fixture
def sample_repository_data():
    """Sample repository data for testing."""
    return {
        "external_id": "123456789",
        "canonical_ref": "github:test-org/test-repo",
        "name": "test-repo",
        "full_name": "test-org/test-repo",
        "description": "A test repository for AI tools",
        "url": "https://github.com/test-org/test-repo",
        "owner": "test-org",
        "stars": 1500,
        "forks": 200,
        "language": "Python",
        "topics": ["machine-learning", "ai", "llm"],
        "trending_rank": 1,
    }


@pytest.fixture
def sample_content_item_data():
    """Sample content item data for testing."""
    return {
        "type": "paper",
        "source": "arxiv",
        "title": "Test Content Item",
        "url": "https://example.com/test",
        "relevance_score": 0.8,
        "importance_score": 0.7,
        "published_at": datetime(2024, 1, 15, 12, 0, 0),
        "tags": ["ai", "ml"],
        "categories": ["agents"],
    }
