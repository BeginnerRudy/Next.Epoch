"""Tests for Pydantic schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from next_epoch.schemas.enums import ContentType, SourceType, DigestType, RunStatus
from next_epoch.schemas.content import (
    Author,
    Paper,
    Repository,
    ContentItem,
    Signal,
    ScoreBreakdown,
    ContentProvenance,
)
from next_epoch.schemas.digest import Digest, DigestSection, DigestStats
from next_epoch.schemas.pagination import Pagination
from next_epoch.schemas.feedback import Feedback, CreateFeedbackRequest
from next_epoch.schemas.run import ProcessingRun


class TestEnums:
    """Test enum definitions."""

    def test_source_type_values(self):
        """Verify all source types are defined."""
        assert SourceType.ARXIV.value == "arxiv"
        assert SourceType.GITHUB.value == "github"
        assert SourceType.TWITTER.value == "twitter"

    def test_content_type_values(self):
        """Verify all content types are defined."""
        assert ContentType.PAPER.value == "paper"
        assert ContentType.REPOSITORY.value == "repository"
        assert ContentType.ARTICLE.value == "article"

    def test_digest_type_values(self):
        """Verify all digest types are defined."""
        assert DigestType.DAILY.value == "daily"
        assert DigestType.WEEKLY.value == "weekly"
        assert DigestType.FLASH.value == "flash"


class TestAuthor:
    """Test Author schema."""

    def test_author_with_all_fields(self):
        """Author with all fields populated."""
        author = Author(
            name="John Doe",
            affiliation="MIT",
            email="john@mit.edu",
            url="https://john.doe.com"
        )
        assert author.name == "John Doe"
        assert author.affiliation == "MIT"

    def test_author_minimal(self):
        """Author with only required fields."""
        author = Author(name="Jane Smith")
        assert author.name == "Jane Smith"
        assert author.affiliation is None


class TestPaper:
    """Test Paper schema."""

    def test_paper_creation(self, sample_paper_data):
        """Create a paper with valid data."""
        paper = Paper(**sample_paper_data)
        assert paper.title == sample_paper_data["title"]
        assert paper.external_id == "2401.12345"
        assert paper.canonical_ref == "arxiv:2401.12345"
        assert len(paper.authors) == 2
        assert paper.source == SourceType.ARXIV

    def test_paper_has_uuid(self, sample_paper_data):
        """Paper should have auto-generated UUID."""
        paper = Paper(**sample_paper_data)
        assert paper.id is not None
        assert len(paper.id) > 0

    def test_paper_missing_required_field(self, sample_paper_data):
        """Paper without required field should fail."""
        del sample_paper_data["title"]
        with pytest.raises(ValidationError):
            Paper(**sample_paper_data)


class TestRepository:
    """Test Repository schema."""

    def test_repository_creation(self, sample_repository_data):
        """Create a repository with valid data."""
        repo = Repository(**sample_repository_data)
        assert repo.name == "test-repo"
        assert repo.full_name == "test-org/test-repo"
        assert repo.stars == 1500
        assert repo.source == SourceType.GITHUB

    def test_repository_defaults(self, sample_repository_data):
        """Repository should have sensible defaults."""
        del sample_repository_data["stars"]
        del sample_repository_data["forks"]
        repo = Repository(**sample_repository_data)
        assert repo.stars == 0
        assert repo.forks == 0


class TestContentItem:
    """Test ContentItem schema."""

    def test_content_item_creation(self, sample_content_item_data):
        """Create a content item with valid data."""
        item = ContentItem(**sample_content_item_data)
        assert item.type == ContentType.PAPER
        assert item.source == SourceType.ARXIV
        assert item.relevance_score == 0.8

    def test_content_item_score_validation(self, sample_content_item_data):
        """Scores must be between 0 and 1."""
        sample_content_item_data["relevance_score"] = 1.5
        with pytest.raises(ValidationError):
            ContentItem(**sample_content_item_data)

    def test_content_item_negative_score(self, sample_content_item_data):
        """Negative scores should fail validation."""
        sample_content_item_data["importance_score"] = -0.1
        with pytest.raises(ValidationError):
            ContentItem(**sample_content_item_data)


class TestSignal:
    """Test Signal schema."""

    def test_signal_string_value(self):
        """Signal with string value."""
        signal = Signal(key="category_match", value="cs.AI")
        assert signal.key == "category_match"
        assert signal.value == "cs.AI"

    def test_signal_numeric_value(self):
        """Signal with numeric value."""
        signal = Signal(key="stars_velocity", value=150.5, weight=0.1)
        assert signal.value == 150.5
        assert signal.weight == 0.1

    def test_signal_boolean_value(self):
        """Signal with boolean value."""
        signal = Signal(key="has_code", value=True, source="github")
        assert signal.value is True
        assert signal.source == "github"


class TestScoreBreakdown:
    """Test ScoreBreakdown schema."""

    def test_score_breakdown_creation(self):
        """Create score breakdown with explanation."""
        breakdown = ScoreBreakdown(
            relevance=0.9,
            importance=0.8,
            novelty=0.7,
            frontier=0.85,
            explanation="High importance: from Anthropic, introduces new benchmark."
        )
        assert breakdown.relevance == 0.9
        assert breakdown.explanation is not None

    def test_score_breakdown_minimal(self):
        """Score breakdown with only required fields."""
        breakdown = ScoreBreakdown(relevance=0.5, importance=0.6)
        assert breakdown.novelty is None
        assert breakdown.frontier is None


class TestPagination:
    """Test Pagination schema."""

    def test_pagination_create(self):
        """Create pagination from page info."""
        pagination = Pagination.create(page=2, per_page=20, total_items=55)
        assert pagination.page == 2
        assert pagination.per_page == 20
        assert pagination.total_items == 55
        assert pagination.total_pages == 3
        assert pagination.has_next is True
        assert pagination.has_prev is True

    def test_pagination_first_page(self):
        """First page should not have prev."""
        pagination = Pagination.create(page=1, per_page=10, total_items=25)
        assert pagination.has_prev is False
        assert pagination.has_next is True

    def test_pagination_last_page(self):
        """Last page should not have next."""
        pagination = Pagination.create(page=3, per_page=10, total_items=25)
        assert pagination.has_prev is True
        assert pagination.has_next is False


class TestFeedback:
    """Test Feedback schemas."""

    def test_create_feedback_request(self):
        """Create feedback request."""
        request = CreateFeedbackRequest(kind="relevance", rating=4, comment="Very relevant!")
        assert request.rating == 4
        assert request.comment == "Very relevant!"

    def test_feedback_rating_bounds(self):
        """Rating must be 1-5."""
        with pytest.raises(ValidationError):
            CreateFeedbackRequest(kind="relevance", rating=0)
        with pytest.raises(ValidationError):
            CreateFeedbackRequest(kind="value", rating=6)


class TestProcessingRun:
    """Test ProcessingRun schema."""

    def test_processing_run_creation(self):
        """Create a processing run."""
        run = ProcessingRun(type="ingest", source="arxiv")
        assert run.type.value == "ingest"
        assert run.status == RunStatus.PENDING
        assert run.id is not None
        assert run.started_at is not None

    def test_processing_run_with_stats(self):
        """Processing run with statistics."""
        run = ProcessingRun(
            type="ingest",
            source="arxiv",
            stats={"items_fetched": 100, "items_created": 95, "duplicates": 5}
        )
        assert run.stats["items_fetched"] == 100
