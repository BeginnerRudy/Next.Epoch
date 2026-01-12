"""Tests for the AI News Collector."""

from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from next_epoch.ingestion.collectors.news import (
    AINewsCollector,
    is_ai_application_story,
    generate_canonical_ref,
    extract_company_from_text,
    APPLICATION_KEYWORDS,
    AI_COMPANIES,
)
from next_epoch.schemas.enums import SourceType


class TestIsAIApplicationStory:
    """Tests for is_ai_application_story function."""

    def test_detects_launch_keyword(self):
        """Articles with 'launches' should be detected."""
        assert is_ai_application_story("OpenAI launches new API", "")
        assert is_ai_application_story("Company Launches AI Tool", "")

    def test_detects_deployment_keywords(self):
        """Articles about deployments should be detected."""
        assert is_ai_application_story("Enterprise deploys AI solution", "")
        assert is_ai_application_story("", "production AI system for customers")

    def test_detects_company_mentions(self):
        """Articles mentioning AI companies should be detected."""
        assert is_ai_application_story("Microsoft announces new feature", "")
        assert is_ai_application_story("", "powered by OpenAI technology")

    def test_rejects_generic_content(self):
        """Generic content without keywords should be rejected."""
        assert not is_ai_application_story("Weather forecast today", "")
        assert not is_ai_application_story("Recipe for chocolate cake", "cooking tips")


class TestGenerateCanonicalRef:
    """Tests for generate_canonical_ref function."""

    def test_generates_consistent_ref(self):
        """Same URL should generate same ref."""
        url = "https://venturebeat.com/ai/some-article/"
        ref1 = generate_canonical_ref("venturebeat", url)
        ref2 = generate_canonical_ref("venturebeat", url)
        assert ref1 == ref2

    def test_different_urls_different_refs(self):
        """Different URLs should generate different refs."""
        url1 = "https://venturebeat.com/ai/article1/"
        url2 = "https://venturebeat.com/ai/article2/"
        ref1 = generate_canonical_ref("venturebeat", url1)
        ref2 = generate_canonical_ref("venturebeat", url2)
        assert ref1 != ref2

    def test_ref_format(self):
        """Ref should have correct format."""
        ref = generate_canonical_ref("venturebeat", "https://example.com/path")
        assert ref.startswith("venturebeat:")
        assert len(ref) > 13  # source: + 12 char hash


class TestExtractCompanyFromText:
    """Tests for extract_company_from_text function."""

    def test_extracts_openai(self):
        """Should extract OpenAI mention."""
        result = extract_company_from_text("OpenAI releases new model")
        assert result == "Openai"

    def test_extracts_anthropic(self):
        """Should extract Anthropic mention."""
        result = extract_company_from_text("Anthropic's Claude gets update")
        assert result == "Anthropic"

    def test_returns_none_for_no_company(self):
        """Should return None when no company found."""
        result = extract_company_from_text("Random text about cooking")
        assert result is None


class TestAINewsCollector:
    """Tests for AINewsCollector class."""

    @pytest.fixture
    def collector(self):
        """Create a collector instance."""
        return AINewsCollector(sources=[SourceType.VENTUREBEAT])

    def test_initialization(self, collector):
        """Collector should initialize correctly."""
        assert collector.sources == [SourceType.VENTUREBEAT]
        assert collector.filter_applications is True
        assert collector.source_name == "ai_news"

    def test_initialization_with_custom_sources(self):
        """Collector should accept custom sources."""
        collector = AINewsCollector(
            sources=[SourceType.TECHCRUNCH],
            filter_applications=False,
        )
        assert collector.sources == [SourceType.TECHCRUNCH]
        assert collector.filter_applications is False

    def test_extract_tags(self, collector):
        """Should extract relevant tags from text."""
        tags = collector._extract_tags(
            "OpenAI launches new LLM for enterprise customers",
            "The chatbot uses generative AI technology"
        )
        assert "openai" in tags
        assert "llm" in tags
        assert "enterprise" in tags
        assert "generative-ai" in tags
        assert "chatbot" in tags

    def test_extract_tags_limits_count(self, collector):
        """Should limit tags to 10."""
        # Create text with many keywords
        title = "OpenAI Anthropic Google Microsoft Nvidia"
        excerpt = "LLM chatbot NLP machine learning computer vision enterprise healthcare finance education"
        tags = collector._extract_tags(title, excerpt)
        assert len(tags) <= 10

    @pytest.mark.asyncio
    async def test_close_closes_client(self, collector):
        """Close should close the HTTP client."""
        await collector.close()
        # Should not raise an error


class TestApplicationKeywords:
    """Tests for application keyword constants."""

    def test_has_launch_keywords(self):
        """Should have launch-related keywords."""
        assert "launches" in APPLICATION_KEYWORDS
        assert "announces" in APPLICATION_KEYWORDS
        assert "deploys" in APPLICATION_KEYWORDS

    def test_has_deployment_keywords(self):
        """Should have deployment-related keywords."""
        assert "enterprise" in APPLICATION_KEYWORDS
        assert "production" in APPLICATION_KEYWORDS
        assert "customers" in APPLICATION_KEYWORDS


class TestAICompanies:
    """Tests for AI company constants."""

    def test_has_major_companies(self):
        """Should have major AI companies."""
        assert "openai" in AI_COMPANIES
        assert "anthropic" in AI_COMPANIES
        assert "google" in AI_COMPANIES
        assert "microsoft" in AI_COMPANIES
        assert "nvidia" in AI_COMPANIES
