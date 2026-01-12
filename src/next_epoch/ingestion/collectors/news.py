"""AI News collector for VentureBeat and TechCrunch."""

import hashlib
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse

import httpx
import structlog
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from next_epoch.config import get_settings
from next_epoch.ingestion.collectors.base import BaseCollector
from next_epoch.schemas.content import Article
from next_epoch.schemas.enums import SourceType

logger = structlog.get_logger()
settings = get_settings()

# VentureBeat AI section
VENTUREBEAT_AI_URL = "https://venturebeat.com/category/ai/"
TECHCRUNCH_AI_URL = "https://techcrunch.com/category/artificial-intelligence/"

# Keywords for filtering AI application/deployment stories
APPLICATION_KEYWORDS = {
    "launches", "announces", "deploys", "releases", "unveils", "introduces",
    "powered by", "uses ai", "ai-powered", "llm-powered", "gpt-powered",
    "enterprise", "production", "customers", "users", "adoption",
    "case study", "implementation", "deployment", "integration",
    "million users", "billion", "revenue", "productivity",
}

# Known AI companies for importance scoring
AI_COMPANIES = {
    "openai", "anthropic", "google", "deepmind", "meta", "microsoft",
    "nvidia", "amazon", "aws", "ibm", "salesforce", "adobe", "oracle",
    "hugging face", "stability ai", "midjourney", "cohere", "replicate",
    "langchain", "pinecone", "weaviate", "databricks", "snowflake",
    "notion", "stripe", "shopify", "slack", "zoom", "github", "copilot",
}


def generate_canonical_ref(source: str, url: str) -> str:
    """Generate a stable canonical reference from URL."""
    parsed = urlparse(url)
    # Use path as the unique identifier
    path = parsed.path.rstrip("/")
    # Create a hash of the path for shorter refs
    path_hash = hashlib.md5(path.encode()).hexdigest()[:12]
    return f"{source}:{path_hash}"


def is_ai_application_story(title: str, excerpt: str) -> bool:
    """Check if article is about AI applications/deployments vs pure research."""
    text = f"{title} {excerpt}".lower()

    # Check for application keywords
    for keyword in APPLICATION_KEYWORDS:
        if keyword in text:
            return True

    # Check for company mentions
    for company in AI_COMPANIES:
        if company in text:
            return True

    return False


def extract_company_from_text(text: str) -> str | None:
    """Extract company name from article text."""
    text_lower = text.lower()
    for company in AI_COMPANIES:
        if company in text_lower:
            # Return proper case version
            return company.title()
    return None


def parse_venturebeat_article(article_elem: BeautifulSoup, base_url: str) -> dict | None:
    """Parse a single article from VentureBeat AI section."""
    try:
        # Find title and link
        title_elem = article_elem.find("h2") or article_elem.find("h3")
        if not title_elem:
            return None

        link_elem = title_elem.find("a") or article_elem.find("a")
        if not link_elem:
            return None

        title = title_elem.get_text(strip=True)
        url = link_elem.get("href", "")
        if not url.startswith("http"):
            url = urljoin(base_url, url)

        # Find excerpt/description
        excerpt_elem = article_elem.find("p") or article_elem.find(class_=re.compile(r"excerpt|description|summary", re.I))
        excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else ""

        # Find author
        author_elem = article_elem.find(class_=re.compile(r"author|byline", re.I))
        author = author_elem.get_text(strip=True) if author_elem else None

        # Find date
        time_elem = article_elem.find("time")
        date_str = time_elem.get("datetime") if time_elem else None
        published_at = None
        if date_str:
            try:
                published_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        if not published_at:
            published_at = datetime.utcnow()

        # Find image
        img_elem = article_elem.find("img")
        image_url = img_elem.get("src") if img_elem else None

        return {
            "title": title,
            "url": url,
            "excerpt": excerpt[:500] if excerpt else "",
            "author": author,
            "published_at": published_at,
            "image_url": image_url,
        }
    except Exception as e:
        logger.warning("Failed to parse VentureBeat article", error=str(e))
        return None


def parse_techcrunch_article(article_elem: BeautifulSoup, base_url: str) -> dict | None:
    """Parse a single article from TechCrunch AI section."""
    try:
        # Find title and link
        title_elem = article_elem.find("h2") or article_elem.find("h3")
        if not title_elem:
            return None

        link_elem = title_elem.find("a") or article_elem.find("a")
        if not link_elem:
            return None

        title = link_elem.get_text(strip=True) or title_elem.get_text(strip=True)
        url = link_elem.get("href", "")
        if not url.startswith("http"):
            url = urljoin(base_url, url)

        # Find excerpt
        excerpt_elem = article_elem.find(class_=re.compile(r"excerpt|deck", re.I)) or article_elem.find("p")
        excerpt = excerpt_elem.get_text(strip=True) if excerpt_elem else ""

        # Find author
        author_elem = article_elem.find(class_=re.compile(r"author", re.I))
        author = author_elem.get_text(strip=True) if author_elem else None

        # Find date
        time_elem = article_elem.find("time")
        date_str = time_elem.get("datetime") if time_elem else None
        published_at = None
        if date_str:
            try:
                published_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        if not published_at:
            published_at = datetime.utcnow()

        # Find image
        img_elem = article_elem.find("img")
        image_url = img_elem.get("src") if img_elem else None

        return {
            "title": title,
            "url": url,
            "excerpt": excerpt[:500] if excerpt else "",
            "author": author,
            "published_at": published_at,
            "image_url": image_url,
        }
    except Exception as e:
        logger.warning("Failed to parse TechCrunch article", error=str(e))
        return None


class AINewsCollector(BaseCollector[Article]):
    """Collector for AI news from VentureBeat and TechCrunch."""

    source_name = "ai_news"

    def __init__(
        self,
        sources: list[SourceType] | None = None,
        filter_applications: bool = True,
    ):
        """Initialize the collector.

        Args:
            sources: List of news sources to scrape (default: VentureBeat)
            filter_applications: Only include AI application/deployment stories
        """
        self.sources = sources or [SourceType.VENTUREBEAT]
        self.filter_applications = filter_applications
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            follow_redirects=True,
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def fetch_page(
        self,
        source: SourceType = SourceType.VENTUREBEAT,
        page: int = 1,
    ) -> list[Article]:
        """Fetch a page of articles from the specified source."""
        if source == SourceType.VENTUREBEAT:
            url = VENTUREBEAT_AI_URL
            if page > 1:
                url = f"{url}page/{page}/"
            parser = parse_venturebeat_article
        elif source == SourceType.TECHCRUNCH:
            url = TECHCRUNCH_AI_URL
            if page > 1:
                url = f"{url}page/{page}/"
            parser = parse_techcrunch_article
        else:
            raise ValueError(f"Unsupported news source: {source}")

        logger.debug(
            "Fetching AI news",
            source=source.value,
            page=page,
            url=url,
        )

        response = await self.client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Find article elements (common patterns)
        articles_found = []

        # Try different article selectors
        article_selectors = [
            "article",
            ".post",
            ".article-card",
            ".story-card",
            '[class*="article"]',
            '[class*="post-"]',
        ]

        for selector in article_selectors:
            articles_found = soup.select(selector)
            if articles_found:
                break

        if not articles_found:
            # Fallback: try finding any element with links that look like articles
            articles_found = soup.find_all("article")

        articles = []
        for article_elem in articles_found[:20]:  # Limit to 20 per page
            article_data = parser(article_elem, url)
            if not article_data:
                continue

            # Apply application filter
            if self.filter_applications:
                if not is_ai_application_story(article_data["title"], article_data["excerpt"]):
                    continue

            # Create Article object
            article = Article(
                source=source,
                external_id=generate_canonical_ref(source.value, article_data["url"]),
                canonical_ref=generate_canonical_ref(source.value, article_data["url"]),
                title=article_data["title"],
                author=article_data["author"],
                content=article_data["excerpt"],  # Will fetch full content later if needed
                excerpt=article_data["excerpt"],
                url=article_data["url"],
                image_url=article_data["image_url"],
                published_at=article_data["published_at"],
                tags=self._extract_tags(article_data["title"], article_data["excerpt"]),
            )
            articles.append(article)

        logger.info(
            "Fetched AI news page",
            source=source.value,
            page=page,
            total_found=len(articles_found),
            after_filter=len(articles),
        )

        return articles

    def _extract_tags(self, title: str, excerpt: str) -> list[str]:
        """Extract tags from article title and excerpt."""
        text = f"{title} {excerpt}".lower()
        tags = []

        # Check for company mentions
        for company in AI_COMPANIES:
            if company in text:
                tags.append(company.replace(" ", "-"))

        # Check for common AI topics
        topic_keywords = {
            "llm": "llm",
            "large language model": "llm",
            "chatbot": "chatbot",
            "generative ai": "generative-ai",
            "machine learning": "machine-learning",
            "computer vision": "computer-vision",
            "nlp": "nlp",
            "automation": "automation",
            "enterprise": "enterprise",
            "healthcare": "healthcare",
            "finance": "finance",
            "education": "education",
        }

        for keyword, tag in topic_keywords.items():
            if keyword in text and tag not in tags:
                tags.append(tag)

        return tags[:10]  # Limit to 10 tags

    async def collect(
        self,
        sources: list[SourceType] | None = None,
        max_pages: int = 2,
    ) -> list[Article]:
        """Collect articles from all configured sources.

        Args:
            sources: Sources to scrape (default: configured sources)
            max_pages: Maximum pages per source

        Returns:
            List of Article objects
        """
        sources = sources or self.sources

        logger.info(
            "Starting AI news collection",
            sources=[s.value for s in sources],
            max_pages=max_pages,
        )

        all_articles = []
        seen_urls = set()

        for source in sources:
            for page in range(1, max_pages + 1):
                try:
                    articles = await self.fetch_page(source=source, page=page)

                    # Deduplicate by URL
                    for article in articles:
                        if article.url not in seen_urls:
                            seen_urls.add(article.url)
                            all_articles.append(article)

                    # Small delay between requests
                    import asyncio
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(
                        "Failed to fetch news page",
                        source=source.value,
                        page=page,
                        error=str(e),
                    )
                    break  # Stop pagination for this source on error

        logger.info(
            "AI news collection complete",
            total_articles=len(all_articles),
            sources=[s.value for s in sources],
        )

        return all_articles
