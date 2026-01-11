"""Tests for scoring functions."""

import pytest
from datetime import datetime, timedelta

from next_epoch.schemas.content import Paper, Repository, ContentItem, Author
from next_epoch.schemas.enums import ContentType, SourceType
from next_epoch.intelligence.relevance import (
    calculate_keyword_density,
    calculate_category_match,
    score_paper_relevance,
    score_repository_relevance,
)
from next_epoch.intelligence.importance import (
    check_author_authority,
    check_has_code,
    check_has_dataset,
    calculate_stars_velocity_score,
    score_paper_importance,
    score_repository_importance,
)
from next_epoch.intelligence.scorer import (
    calculate_recency_boost,
    calculate_frontier_score,
    score_content,
)


class TestKeywordDensity:
    """Test keyword density calculation."""

    def test_high_density_text(self):
        """Text with many AI keywords gets high score."""
        text = "This paper presents a transformer-based LLM for machine learning with deep neural networks"
        density = calculate_keyword_density(text)
        assert density >= 0.6

    def test_low_density_text(self):
        """Text with few AI keywords gets low score."""
        text = "A study on web development using JavaScript and React"
        density = calculate_keyword_density(text)
        assert density < 0.3

    def test_empty_text(self):
        """Empty text returns 0."""
        assert calculate_keyword_density("") == 0.0


class TestCategoryMatch:
    """Test category match calculation."""

    def test_primary_ai_category(self):
        """Primary AI categories get full score."""
        assert calculate_category_match(["cs.AI", "cs.LG"]) == 1.0

    def test_secondary_category(self):
        """Secondary relevant categories get partial score."""
        assert calculate_category_match(["cs.CV"]) >= 0.8

    def test_no_match(self):
        """Non-relevant categories get zero."""
        assert calculate_category_match(["math.NA"]) == 0.0

    def test_empty_categories(self):
        """Empty categories return 0."""
        assert calculate_category_match([]) == 0.0


class TestAuthorAuthority:
    """Test author authority detection."""

    def test_known_lab_affiliation(self):
        """Authors from known labs get high score."""
        authors = [
            {"name": "John Doe", "affiliation": "OpenAI"},
            {"name": "Jane Smith", "affiliation": "Stanford University"},
        ]
        score, matched = check_author_authority(authors)
        assert score >= 0.5
        assert len(matched) > 0

    def test_unknown_affiliation(self):
        """Authors from unknown affiliations get low score."""
        authors = [
            {"name": "John Doe", "affiliation": "Unknown University"},
        ]
        score, matched = check_author_authority(authors)
        assert score == 0.0
        assert len(matched) == 0


class TestCodeDetection:
    """Test code availability detection."""

    def test_github_link(self):
        """GitHub link detected."""
        text = "Code is available at github.com/author/repo"
        assert check_has_code(text) is True

    def test_open_source_mention(self):
        """Open source mention detected."""
        text = "We release our implementation as open-source"
        assert check_has_code(text) is True

    def test_no_code(self):
        """No code mention returns False."""
        text = "This is a theoretical paper with no implementation"
        assert check_has_code(text) is False


class TestStarsVelocity:
    """Test stars velocity scoring."""

    def test_high_stars(self):
        """High star count gets high score."""
        score = calculate_stars_velocity_score(15000)
        assert score == 1.0

    def test_medium_stars(self):
        """Medium star count gets medium score."""
        score = calculate_stars_velocity_score(800)
        assert 0.3 <= score <= 0.7

    def test_trending_boost(self):
        """Trending rank boosts score."""
        base_score = calculate_stars_velocity_score(500)
        boosted_score = calculate_stars_velocity_score(500, trending_rank=5)
        assert boosted_score > base_score


class TestRecencyBoost:
    """Test recency boost calculation."""

    def test_recent_content(self):
        """Content published recently gets high boost."""
        published = datetime.utcnow() - timedelta(hours=6)
        boost = calculate_recency_boost(published)
        assert boost >= 0.9

    def test_week_old_content(self):
        """Week-old content gets low boost."""
        published = datetime.utcnow() - timedelta(days=7)
        boost = calculate_recency_boost(published)
        assert boost <= 0.1

    def test_old_content(self):
        """Old content gets zero boost."""
        published = datetime.utcnow() - timedelta(days=30)
        boost = calculate_recency_boost(published)
        assert boost == 0.0


class TestFrontierScore:
    """Test frontier score calculation."""

    def test_high_scores(self):
        """High component scores give high frontier score."""
        frontier = calculate_frontier_score(
            relevance=0.9,
            importance=0.9,
            novelty=0.9,
            recency_boost=0.9,
        )
        assert frontier >= 0.85

    def test_low_scores(self):
        """Low component scores give low frontier score."""
        frontier = calculate_frontier_score(
            relevance=0.2,
            importance=0.2,
            novelty=0.2,
            recency_boost=0.2,
        )
        assert frontier <= 0.3

    def test_no_novelty(self):
        """Works without novelty score."""
        frontier = calculate_frontier_score(
            relevance=0.8,
            importance=0.8,
            novelty=None,
            recency_boost=0.8,
        )
        assert 0.7 <= frontier <= 0.9


class TestPaperScoring:
    """Test paper scoring integration."""

    def test_relevant_paper(self, sample_paper_data):
        """AI paper gets high relevance score."""
        paper = Paper(**sample_paper_data)
        result = score_paper_relevance(paper)
        assert result.score >= 0.5

    def test_paper_importance(self, sample_paper_data):
        """Paper importance scoring works."""
        paper = Paper(**sample_paper_data)
        result = score_paper_importance(paper)
        assert 0.0 <= result.score <= 1.0
        assert len(result.signals) > 0


class TestRepositoryScoring:
    """Test repository scoring integration."""

    def test_ai_repo_relevance(self, sample_repository_data):
        """AI-related repo gets good relevance."""
        repo = Repository(**sample_repository_data)
        result = score_repository_relevance(repo)
        assert result.score >= 0.3

    def test_repo_importance(self, sample_repository_data):
        """Repository importance based on stars."""
        repo = Repository(**sample_repository_data)
        result = score_repository_importance(repo)
        assert result.score >= 0.3
