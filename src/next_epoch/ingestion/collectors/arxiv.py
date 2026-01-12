"""arXiv API collector."""

import re
from datetime import datetime
from urllib.parse import urlencode

import httpx
import feedparser
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from next_epoch.config import get_settings
from next_epoch.ingestion.collectors.base import BaseCollector
from next_epoch.schemas.content import Author, Paper

logger = structlog.get_logger()
settings = get_settings()


# arXiv API base URL (HTTPS required)
ARXIV_API_URL = "https://export.arxiv.org/api/query"

# arXiv ID pattern
ARXIV_ID_PATTERN = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?$")


def parse_arxiv_id(url: str) -> str | None:
    """Extract arXiv ID from URL or ID string."""
    # Try to match the pattern
    match = ARXIV_ID_PATTERN.search(url)
    if match:
        return match.group(1)
    return None


def parse_author(author_data: dict) -> Author:
    """Parse author from arXiv entry."""
    name = author_data.get("name", "Unknown")
    # arXiv doesn't provide affiliation in the API consistently
    return Author(name=name)


def parse_categories(entry: dict) -> list[str]:
    """Extract categories from arXiv entry."""
    categories = []

    # Primary category
    if "arxiv_primary_category" in entry:
        primary = entry["arxiv_primary_category"]
        if isinstance(primary, dict) and "term" in primary:
            categories.append(primary["term"])

    # All categories
    tags = entry.get("tags", [])
    for tag in tags:
        if isinstance(tag, dict) and "term" in tag:
            term = tag["term"]
            if term not in categories:
                categories.append(term)

    return categories


def parse_entry(entry: dict) -> Paper | None:
    """Parse a feedparser entry into a Paper schema."""
    try:
        # Extract arXiv ID from entry ID URL
        entry_id = entry.get("id", "")
        arxiv_id = parse_arxiv_id(entry_id)

        if not arxiv_id:
            logger.warning("Could not parse arXiv ID", entry_id=entry_id)
            return None

        # Parse dates
        published_str = entry.get("published", "")
        updated_str = entry.get("updated", "")

        # feedparser parses to time struct, convert to datetime
        published_at = datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") and entry.published_parsed else datetime.utcnow()
        updated_at = datetime(*entry.updated_parsed[:6]) if hasattr(entry, "updated_parsed") and entry.updated_parsed else None

        # Get links
        url = f"https://arxiv.org/abs/{arxiv_id}"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        # Check for actual PDF link
        links = entry.get("links", [])
        for link in links:
            if isinstance(link, dict):
                if link.get("type") == "application/pdf":
                    pdf_url = link.get("href", pdf_url)

        # Parse authors
        authors = []
        author_data = entry.get("authors", [])
        for author in author_data:
            if isinstance(author, dict):
                authors.append(parse_author(author))

        # If no authors found, try single author field
        if not authors and "author" in entry:
            authors.append(Author(name=entry["author"]))

        # Get abstract/summary
        abstract = entry.get("summary", "").strip()
        # Clean up the abstract (arXiv sometimes has extra whitespace)
        abstract = " ".join(abstract.split())

        # Parse categories
        categories = parse_categories(entry)

        return Paper(
            external_id=arxiv_id,
            canonical_ref=f"arxiv:{arxiv_id}",
            title=entry.get("title", "").replace("\n", " ").strip(),
            authors=authors,
            abstract=abstract,
            url=url,
            pdf_url=pdf_url,
            published_at=published_at,
            updated_at=updated_at,
            categories=categories,
            tags=[],  # Will be populated by enrichment
        )
    except Exception as e:
        logger.error("Failed to parse arXiv entry", error=str(e), entry_id=entry.get("id"))
        return None


class ArxivCollector(BaseCollector[Paper]):
    """Collector for arXiv papers via the arXiv API."""

    source_name = "arxiv"

    def __init__(
        self,
        categories: list[str] | None = None,
        max_results: int | None = None,
    ):
        self.categories = categories or settings.arxiv_categories
        self.max_results = max_results or settings.arxiv_max_results

        # Configure HTTP client with optional proxy for China network access
        client_kwargs = {"timeout": 30.0}
        if settings.http_proxy:
            client_kwargs["proxy"] = settings.http_proxy
            logger.info("arXiv collector using proxy", proxy=settings.http_proxy)
        self.client = httpx.AsyncClient(**client_kwargs)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def _build_query(self, categories: list[str]) -> str:
        """Build arXiv search query for given categories."""
        # Build category query: cat:cs.AI OR cat:cs.LG OR ...
        cat_queries = [f"cat:{cat}" for cat in categories]
        return " OR ".join(cat_queries)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def fetch_page(
        self,
        query: str,
        start: int = 0,
        max_results: int = 100,
    ) -> list[Paper]:
        """Fetch a page of papers from arXiv API."""
        params = {
            "search_query": query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        url = f"{ARXIV_API_URL}?{urlencode(params)}"

        logger.debug(
            "Fetching arXiv page",
            query=query,
            start=start,
            max_results=max_results,
        )

        response = await self.client.get(url)
        response.raise_for_status()

        # Parse the Atom feed
        feed = feedparser.parse(response.text)

        papers = []
        for entry in feed.entries:
            paper = parse_entry(entry)
            if paper:
                papers.append(paper)

        logger.info(
            "Fetched arXiv page",
            papers_count=len(papers),
            start=start,
        )

        return papers

    async def collect(
        self,
        max_results: int | None = None,
        categories: list[str] | None = None,
    ) -> list[Paper]:
        """Collect papers from arXiv.

        Args:
            max_results: Maximum number of papers to fetch
            categories: arXiv categories to query (e.g., ["cs.AI", "cs.LG"])

        Returns:
            List of Paper objects
        """
        max_results = max_results or self.max_results
        categories = categories or self.categories

        query = self._build_query(categories)

        logger.info(
            "Starting arXiv collection",
            categories=categories,
            max_results=max_results,
        )

        all_papers = []
        page_size = min(100, max_results)  # arXiv recommends max 100 per request
        start = 0

        while len(all_papers) < max_results:
            remaining = max_results - len(all_papers)
            fetch_size = min(page_size, remaining)

            papers = await self.fetch_page(query, start=start, max_results=fetch_size)

            if not papers:
                break

            all_papers.extend(papers)
            start += len(papers)

            # arXiv rate limiting: wait between requests
            if len(all_papers) < max_results:
                import asyncio
                await asyncio.sleep(3)  # arXiv recommends 3 second delay

        logger.info(
            "arXiv collection complete",
            total_papers=len(all_papers),
            categories=categories,
        )

        return all_papers
