"""GitHub Trending collector."""

import re
from datetime import datetime

import httpx
import structlog
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from next_epoch.config import get_settings
from next_epoch.ingestion.collectors.base import BaseCollector
from next_epoch.schemas.content import Repository

logger = structlog.get_logger()
settings = get_settings()

# GitHub Trending URL
GITHUB_TRENDING_URL = "https://github.com/trending"

# AI-related keywords for filtering
AI_KEYWORDS = {
    "llm", "gpt", "transformer", "neural", "deep-learning", "machine-learning",
    "reinforcement-learning", "nlp", "computer-vision", "diffusion", "generative-ai",
    "rag", "agent", "embedding", "fine-tuning", "inference", "benchmark",
    "langchain", "llamaindex", "openai", "anthropic", "huggingface",
    "pytorch", "tensorflow", "jax", "keras", "stable-diffusion",
    "chatgpt", "claude", "gemini", "mistral", "llama", "whisper",
    "ai", "ml", "artificial-intelligence", "deep-neural-network",
}


def is_ai_related(repo_data: dict) -> bool:
    """Check if a repository is AI-related based on topics and description."""
    # Check topics
    topics = set(repo_data.get("topics", []))
    if topics & AI_KEYWORDS:
        return True

    # Check language (common AI languages)
    language = (repo_data.get("language") or "").lower()
    if language in {"python", "jupyter notebook"}:
        # Further check description for AI keywords
        description = (repo_data.get("description") or "").lower()
        name = repo_data.get("name", "").lower()

        text_to_check = f"{description} {name}"
        for keyword in AI_KEYWORDS:
            if keyword.replace("-", " ") in text_to_check or keyword in text_to_check:
                return True

    return False


def parse_stars(stars_text: str) -> int:
    """Parse stars count from text like '1.2k' or '15,234'."""
    if not stars_text:
        return 0

    stars_text = stars_text.strip().lower().replace(",", "")

    if "k" in stars_text:
        return int(float(stars_text.replace("k", "")) * 1000)
    elif "m" in stars_text:
        return int(float(stars_text.replace("m", "")) * 1000000)

    try:
        return int(stars_text)
    except ValueError:
        return 0


def parse_trending_repo(article: BeautifulSoup, rank: int) -> dict | None:
    """Parse a single trending repository from HTML article element."""
    try:
        # Get repo link
        h2 = article.find("h2")
        if not h2:
            return None

        link = h2.find("a")
        if not link:
            return None

        full_name = link.get("href", "").strip("/")
        if "/" not in full_name:
            return None

        owner, name = full_name.split("/", 1)

        # Get description
        desc_p = article.find("p", class_=lambda x: x and "color-fg-muted" in str(x))
        description = desc_p.get_text(strip=True) if desc_p else None

        # Get language
        lang_span = article.find("span", itemprop="programmingLanguage")
        language = lang_span.get_text(strip=True) if lang_span else None

        # Get stars
        stars_link = article.find("a", href=lambda x: x and "/stargazers" in str(x))
        stars = 0
        if stars_link:
            stars = parse_stars(stars_link.get_text(strip=True))

        # Get forks
        forks_link = article.find("a", href=lambda x: x and "/forks" in str(x))
        forks = 0
        if forks_link:
            forks = parse_stars(forks_link.get_text(strip=True))

        # Get stars today
        stars_today_span = article.find("span", class_=lambda x: x and "d-inline-block" in str(x))
        stars_today = 0
        if stars_today_span and "stars" in stars_today_span.get_text().lower():
            stars_text = stars_today_span.get_text(strip=True)
            match = re.search(r"([\d,]+)", stars_text)
            if match:
                stars_today = parse_stars(match.group(1))

        return {
            "full_name": full_name,
            "owner": owner,
            "name": name,
            "description": description,
            "language": language,
            "stars": stars,
            "forks": forks,
            "stars_today": stars_today,
            "trending_rank": rank,
            "url": f"https://github.com/{full_name}",
        }
    except Exception as e:
        logger.warning("Failed to parse trending repo", error=str(e))
        return None


class GitHubTrendingCollector(BaseCollector[Repository]):
    """Collector for GitHub Trending repositories."""

    source_name = "github"

    def __init__(
        self,
        languages: list[str] | None = None,
        filter_ai: bool = True,
    ):
        self.languages = languages or settings.github_trending_languages
        self.filter_ai = filter_ai
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
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
        language: str | None = None,
        since: str = "daily",
    ) -> list[Repository]:
        """Fetch trending repositories for a language."""
        url = GITHUB_TRENDING_URL
        if language:
            url = f"{url}/{language}"

        params = {"since": since}

        logger.debug(
            "Fetching GitHub Trending",
            language=language or "all",
            since=since,
        )

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Find all repository articles
        articles = soup.find_all("article", class_="Box-row")

        repos = []
        for rank, article in enumerate(articles, 1):
            repo_data = parse_trending_repo(article, rank)
            if not repo_data:
                continue

            # Apply AI filter if enabled
            if self.filter_ai and not is_ai_related(repo_data):
                continue

            # Convert to Repository schema
            repo = Repository(
                external_id=repo_data["full_name"],  # Use full_name as external ID
                canonical_ref=f"github:{repo_data['full_name']}",
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                description=repo_data["description"],
                url=repo_data["url"],
                owner=repo_data["owner"],
                stars=repo_data["stars"],
                forks=repo_data["forks"],
                language=repo_data["language"],
                topics=[],  # Not available from trending page
                trending_rank=repo_data["trending_rank"],
                trending_since=datetime.utcnow(),
            )
            repos.append(repo)

        logger.info(
            "Fetched GitHub Trending",
            language=language or "all",
            total_found=len(articles),
            ai_filtered=len(repos),
        )

        return repos

    async def fetch_repo_details(self, full_name: str) -> dict | None:
        """Fetch additional repository details from GitHub API."""
        # Note: This would require GitHub API token for higher rate limits
        # For MVP, we'll skip this and use just the trending page data
        return None

    async def collect(
        self,
        languages: list[str] | None = None,
        filter_ai: bool | None = None,
    ) -> list[Repository]:
        """Collect trending repositories.

        Args:
            languages: List of languages to check (empty string = all)
            filter_ai: Whether to filter for AI-related repos only

        Returns:
            List of Repository objects
        """
        languages = languages or self.languages
        filter_ai = filter_ai if filter_ai is not None else self.filter_ai

        logger.info(
            "Starting GitHub Trending collection",
            languages=languages,
            filter_ai=filter_ai,
        )

        all_repos = []
        seen_repos = set()

        for language in languages:
            try:
                repos = await self.fetch_page(language=language if language else None)

                # Deduplicate across language pages
                for repo in repos:
                    if repo.full_name not in seen_repos:
                        seen_repos.add(repo.full_name)
                        all_repos.append(repo)

                # Small delay between requests
                import asyncio
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(
                    "Failed to fetch trending for language",
                    language=language,
                    error=str(e),
                )

        logger.info(
            "GitHub Trending collection complete",
            total_repos=len(all_repos),
            languages=languages,
        )

        return all_repos
