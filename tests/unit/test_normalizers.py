"""Tests for content normalizers."""

import pytest
from datetime import datetime

from next_epoch.schemas.content import Paper, Repository, Author
from next_epoch.schemas.enums import ContentType, SourceType
from next_epoch.ingestion.normalizers import (
    normalize_content,
    normalize_paper,
    normalize_repository,
)


class TestNormalizePaper:
    """Test paper normalization."""

    def test_normalize_paper(self, sample_paper_data):
        """Normalize a paper to ContentItem."""
        paper = Paper(**sample_paper_data)
        content = normalize_paper(paper)

        assert content.type == ContentType.PAPER
        assert content.source == SourceType.ARXIV
        assert content.title == paper.title
        assert content.url == paper.url
        assert content.published_at == paper.published_at
        assert content.provenance is not None
        assert content.provenance.parser == "arxiv_normalizer"

    def test_normalize_paper_preserves_categories(self, sample_paper_data):
        """Paper categories become ContentItem categories."""
        paper = Paper(**sample_paper_data)
        content = normalize_paper(paper)

        assert content.categories == paper.categories


class TestNormalizeRepository:
    """Test repository normalization."""

    def test_normalize_repository(self, sample_repository_data):
        """Normalize a repository to ContentItem."""
        repo = Repository(**sample_repository_data)
        content = normalize_repository(repo)

        assert content.type == ContentType.REPOSITORY
        assert content.source == SourceType.GITHUB
        assert repo.full_name in content.title
        assert content.url == repo.url
        assert content.provenance is not None
        assert content.provenance.parser == "github_normalizer"

    def test_normalize_repository_adds_language_tag(self, sample_repository_data):
        """Repository language is added as a tag."""
        repo = Repository(**sample_repository_data)
        content = normalize_repository(repo)

        assert "python" in content.tags


class TestNormalizeContent:
    """Test generic normalize_content function."""

    def test_normalize_paper_via_generic(self, sample_paper_data):
        """Generic normalizer handles Paper."""
        paper = Paper(**sample_paper_data)
        content = normalize_content(paper)
        assert content.type == ContentType.PAPER

    def test_normalize_repo_via_generic(self, sample_repository_data):
        """Generic normalizer handles Repository."""
        repo = Repository(**sample_repository_data)
        content = normalize_content(repo)
        assert content.type == ContentType.REPOSITORY

    def test_unknown_type_raises(self):
        """Unknown type raises ValueError."""
        with pytest.raises(ValueError):
            normalize_content("not a valid content type")
