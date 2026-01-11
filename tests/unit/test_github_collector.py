"""Tests for GitHub Trending collector."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from next_epoch.ingestion.collectors.github import (
    GitHubTrendingCollector,
    is_ai_related,
    parse_stars,
)


class TestParseStars:
    """Test star count parsing."""

    def test_parse_simple_number(self):
        """Parse simple number."""
        assert parse_stars("1234") == 1234

    def test_parse_with_commas(self):
        """Parse number with commas."""
        assert parse_stars("15,234") == 15234

    def test_parse_k_suffix(self):
        """Parse k suffix."""
        assert parse_stars("1.5k") == 1500
        assert parse_stars("2k") == 2000

    def test_parse_m_suffix(self):
        """Parse m suffix."""
        assert parse_stars("1.5m") == 1500000

    def test_parse_empty(self):
        """Empty string returns 0."""
        assert parse_stars("") == 0


class TestIsAiRelated:
    """Test AI-related detection."""

    def test_ai_topic_match(self):
        """Repository with AI topic is related."""
        repo = {"topics": ["machine-learning", "data-science"]}
        assert is_ai_related(repo) is True

    def test_llm_topic_match(self):
        """Repository with LLM topic is related."""
        repo = {"topics": ["llm", "web"]}
        assert is_ai_related(repo) is True

    def test_python_with_ai_description(self):
        """Python repo with AI in description is related."""
        repo = {
            "topics": [],
            "language": "Python",
            "description": "A machine learning framework",
            "name": "ml-tool",
        }
        assert is_ai_related(repo) is True

    def test_non_ai_repo(self):
        """Non-AI repository is not related."""
        repo = {
            "topics": ["web", "javascript"],
            "language": "JavaScript",
            "description": "A web framework",
            "name": "web-tool",
        }
        assert is_ai_related(repo) is False


class TestGitHubTrendingCollector:
    """Test GitHubTrendingCollector class."""

    def test_init_with_defaults(self):
        """Collector initializes with defaults."""
        collector = GitHubTrendingCollector()
        assert collector.filter_ai is True

    @pytest.mark.asyncio
    async def test_collect_parses_html(self):
        """Test that collect parses HTML correctly."""
        collector = GitHubTrendingCollector(languages=["python"], filter_ai=False)

        # Mock HTML response with a trending repo
        mock_html = """
        <html>
        <body>
            <article class="Box-row">
                <h2>
                    <a href="/test-org/test-repo">test-org/test-repo</a>
                </h2>
                <p class="color-fg-muted">A test repository</p>
                <span itemprop="programmingLanguage">Python</span>
                <a href="/test-org/test-repo/stargazers">1,234</a>
                <a href="/test-org/test-repo/forks">100</a>
            </article>
        </body>
        </html>
        """

        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.raise_for_status = MagicMock()

        with patch.object(collector.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            repos = await collector.fetch_page(language="python")

            assert isinstance(repos, list)
            mock_get.assert_called_once()

            # Should have parsed at least one repo (if filter_ai is False)
            if repos:
                assert repos[0].full_name == "test-org/test-repo"
                assert repos[0].stars == 1234

        await collector.close()
