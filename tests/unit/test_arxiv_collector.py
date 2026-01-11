"""Tests for arXiv collector."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from next_epoch.ingestion.collectors.arxiv import (
    ArxivCollector,
    parse_arxiv_id,
    parse_entry,
    parse_author,
)


class TestParseArxivId:
    """Test arXiv ID parsing."""

    def test_parse_from_url(self):
        """Parse arXiv ID from URL."""
        url = "http://arxiv.org/abs/2401.12345v1"
        assert parse_arxiv_id(url) == "2401.12345"

    def test_parse_short_id(self):
        """Parse short arXiv ID."""
        url = "http://arxiv.org/abs/2401.1234"
        assert parse_arxiv_id(url) == "2401.1234"

    def test_parse_without_version(self):
        """Parse ID without version."""
        url = "http://arxiv.org/abs/2401.12345"
        assert parse_arxiv_id(url) == "2401.12345"

    def test_invalid_url(self):
        """Invalid URL returns None."""
        assert parse_arxiv_id("not-a-valid-url") is None


class TestParseAuthor:
    """Test author parsing."""

    def test_parse_author_with_name(self):
        """Parse author with name."""
        author = parse_author({"name": "John Doe"})
        assert author.name == "John Doe"
        assert author.affiliation is None


class TestParseEntry:
    """Test feedparser entry parsing."""

    def test_parse_valid_entry(self):
        """Parse a valid arXiv entry."""
        entry = MagicMock()
        entry.id = "http://arxiv.org/abs/2401.12345v1"
        entry.title = "Test Paper Title"
        entry.summary = "This is the abstract of the paper."
        entry.published_parsed = (2024, 1, 15, 12, 0, 0, 0, 0, 0)
        entry.updated_parsed = (2024, 1, 16, 12, 0, 0, 0, 0, 0)
        entry.authors = [{"name": "John Doe"}, {"name": "Jane Smith"}]
        entry.links = [{"href": "http://arxiv.org/pdf/2401.12345.pdf", "type": "application/pdf"}]
        entry.arxiv_primary_category = {"term": "cs.AI"}
        entry.tags = [{"term": "cs.AI"}, {"term": "cs.LG"}]

        # Set up get method for dict-like access
        entry.get = lambda key, default=None: getattr(entry, key, default) if hasattr(entry, key) else default

        paper = parse_entry(entry)

        assert paper is not None
        assert paper.external_id == "2401.12345"
        assert paper.canonical_ref == "arxiv:2401.12345"
        assert paper.title == "Test Paper Title"
        assert len(paper.authors) == 2


class TestArxivCollector:
    """Test ArxivCollector class."""

    def test_build_query(self):
        """Test query building."""
        collector = ArxivCollector(categories=["cs.AI", "cs.LG"])
        query = collector._build_query(["cs.AI", "cs.LG"])
        assert "cat:cs.AI" in query
        assert "cat:cs.LG" in query
        assert " OR " in query

    @pytest.mark.asyncio
    async def test_collect_returns_papers(self):
        """Test that collect returns a list of papers."""
        collector = ArxivCollector(categories=["cs.AI"], max_results=5)

        # Mock the HTTP client
        mock_response = MagicMock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2401.12345v1</id>
                <title>Test Paper</title>
                <summary>Test abstract</summary>
                <published>2024-01-15T12:00:00Z</published>
                <updated>2024-01-15T12:00:00Z</updated>
                <author><name>Test Author</name></author>
                <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cs.AI"/>
            </entry>
        </feed>"""
        mock_response.raise_for_status = MagicMock()

        with patch.object(collector.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            papers = await collector.collect(max_results=1)

            assert isinstance(papers, list)
            # With mocked response, should have at least attempted to parse
            mock_get.assert_called_once()

        await collector.close()
