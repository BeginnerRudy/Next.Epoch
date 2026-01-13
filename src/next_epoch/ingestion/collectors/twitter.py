"""Twitter/X collector for AI influencer tweets using Nitter."""

import hashlib
import re
from datetime import datetime
from urllib.parse import urljoin

import httpx
import structlog
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from next_epoch.config import get_settings
from next_epoch.ingestion.collectors.base import BaseCollector
from next_epoch.schemas.enums import SourceType

logger = structlog.get_logger()
settings = get_settings()

# Nitter instances (Twitter frontend that doesn't require API)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.woodland.cafe",
]

# AI influencers and researchers to follow
AI_INFLUENCERS = [
    "kaborediallo",  # Anthropic
    "sama",  # Sam Altman - OpenAI
    "ylecun",  # Yann LeCun - Meta AI
    "demaboris",  # Dema - AI researcher
    "AndrewYNg",  # Andrew Ng
    "EMostaque",  # Emad Mostaque - Stability AI
    "DrJimFan",  # Jim Fan - NVIDIA
    "ClementDelworkerng",  # Clement Delangue - Hugging Face
    "goodaborside",  # Andrej Karpathy
    "jeffdean",  # Jeff Dean - Google
    "random_aiml",  # AI/ML news
    "huggingface",  # Hugging Face
    "OpenAI",  # OpenAI
    "AnthropicAI",  # Anthropic
    "GoogleAI",  # Google AI
]

# Keywords for filtering AI-relevant tweets
AI_KEYWORDS = {
    "llm", "gpt", "claude", "gemini", "llama", "mistral", "transformer",
    "neural", "deep learning", "machine learning", "ai", "artificial intelligence",
    "model", "training", "inference", "rlhf", "fine-tuning", "finetuning",
    "agent", "reasoning", "benchmark", "open source", "release", "launch",
    "paper", "research", "breakthrough", "sota", "state-of-the-art",
    "multimodal", "vision", "language model", "embedding", "vector",
    "rag", "retrieval", "prompt", "context window", "token",
}


def generate_canonical_ref(username: str, tweet_id: str) -> str:
    """Generate a stable canonical reference for a tweet."""
    return f"twitter:{username}/{tweet_id}"


def extract_tweet_id(url: str) -> str | None:
    """Extract tweet ID from URL."""
    match = re.search(r'/status/(\d+)', url)
    return match.group(1) if match else None


def is_ai_relevant(text: str) -> bool:
    """Check if tweet content is AI-relevant."""
    text_lower = text.lower()
    for keyword in AI_KEYWORDS:
        if keyword in text_lower:
            return True
    return False


def parse_relative_time(time_str: str) -> datetime:
    """Parse relative time like '2h' or '1d' to datetime."""
    now = datetime.utcnow()
    time_str = time_str.strip().lower()

    if 's' in time_str:
        return now
    elif 'm' in time_str and 'mo' not in time_str:
        minutes = int(re.search(r'(\d+)', time_str).group(1))
        from datetime import timedelta
        return now - timedelta(minutes=minutes)
    elif 'h' in time_str:
        hours = int(re.search(r'(\d+)', time_str).group(1))
        from datetime import timedelta
        return now - timedelta(hours=hours)
    elif 'd' in time_str:
        days = int(re.search(r'(\d+)', time_str).group(1))
        from datetime import timedelta
        return now - timedelta(days=days)
    else:
        # Try to parse as date
        try:
            return datetime.strptime(time_str, "%b %d, %Y")
        except ValueError:
            return now


class Tweet:
    """Tweet data structure."""

    def __init__(
        self,
        id: str,
        username: str,
        display_name: str,
        content: str,
        url: str,
        published_at: datetime,
        likes: int = 0,
        retweets: int = 0,
        replies: int = 0,
        is_retweet: bool = False,
        media_urls: list[str] | None = None,
    ):
        self.id = id
        self.username = username
        self.display_name = display_name
        self.content = content
        self.url = url
        self.published_at = published_at
        self.likes = likes
        self.retweets = retweets
        self.replies = replies
        self.is_retweet = is_retweet
        self.media_urls = media_urls or []
        self.canonical_ref = generate_canonical_ref(username, id)
        self.external_id = id


class TwitterCollector(BaseCollector[Tweet]):
    """Collector for AI-related tweets from Twitter/X via Nitter."""

    source_name = "twitter"

    def __init__(
        self,
        influencers: list[str] | None = None,
        filter_ai_relevant: bool = True,
    ):
        """Initialize the collector.

        Args:
            influencers: List of Twitter usernames to follow
            filter_ai_relevant: Only include AI-relevant tweets
        """
        self.influencers = influencers or AI_INFLUENCERS
        self.filter_ai_relevant = filter_ai_relevant
        self.nitter_instance = NITTER_INSTANCES[0]
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

    async def fetch_page(self, username: str | None = None, **kwargs) -> list[Tweet]:
        """Fetch a single page of tweets from a user.

        Args:
            username: Twitter username to fetch tweets from

        Returns:
            List of Tweet objects
        """
        if not username:
            return []
        return await self.fetch_user_tweets(username)

    def _try_next_instance(self):
        """Try the next Nitter instance if current one fails."""
        current_idx = NITTER_INSTANCES.index(self.nitter_instance)
        next_idx = (current_idx + 1) % len(NITTER_INSTANCES)
        self.nitter_instance = NITTER_INSTANCES[next_idx]
        logger.info("Switching Nitter instance", new_instance=self.nitter_instance)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def fetch_user_tweets(self, username: str) -> list[Tweet]:
        """Fetch recent tweets from a user."""
        url = f"{self.nitter_instance}/{username}"

        logger.debug(
            "Fetching tweets",
            username=username,
            url=url,
        )

        try:
            response = await self.client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "Nitter request failed, trying next instance",
                username=username,
                error=str(e),
            )
            self._try_next_instance()
            raise

        soup = BeautifulSoup(response.text, "lxml")
        tweets = []

        # Find tweet containers
        tweet_elements = soup.select(".timeline-item")

        for tweet_elem in tweet_elements[:10]:  # Limit to 10 tweets per user
            try:
                # Skip retweets for now
                if tweet_elem.select_one(".retweet-header"):
                    continue

                # Get tweet content
                content_elem = tweet_elem.select_one(".tweet-content")
                if not content_elem:
                    continue
                content = content_elem.get_text(strip=True)

                # Get tweet link/ID
                link_elem = tweet_elem.select_one(".tweet-link")
                if not link_elem:
                    continue
                tweet_url = link_elem.get("href", "")
                tweet_id = extract_tweet_id(tweet_url)
                if not tweet_id:
                    continue

                # Get username and display name
                username_elem = tweet_elem.select_one(".username")
                fullname_elem = tweet_elem.select_one(".fullname")
                tweet_username = username_elem.get_text(strip=True).lstrip("@") if username_elem else username
                display_name = fullname_elem.get_text(strip=True) if fullname_elem else tweet_username

                # Get timestamp
                time_elem = tweet_elem.select_one(".tweet-date a")
                time_str = time_elem.get("title", "") if time_elem else ""
                if time_str:
                    try:
                        published_at = datetime.strptime(time_str, "%b %d, %Y · %I:%M %p %Z")
                    except ValueError:
                        published_at = parse_relative_time(time_elem.get_text(strip=True) if time_elem else "")
                else:
                    published_at = datetime.utcnow()

                # Get stats
                stats = tweet_elem.select(".tweet-stat")
                likes = 0
                retweets = 0
                replies = 0
                for stat in stats:
                    stat_text = stat.get_text(strip=True)
                    if "like" in stat.get("class", []):
                        likes = int(re.sub(r'\D', '', stat_text) or 0)
                    elif "retweet" in stat.get("class", []):
                        retweets = int(re.sub(r'\D', '', stat_text) or 0)
                    elif "comment" in stat.get("class", []):
                        replies = int(re.sub(r'\D', '', stat_text) or 0)

                # Get media
                media_urls = []
                for img in tweet_elem.select(".attachment img"):
                    src = img.get("src", "")
                    if src:
                        media_urls.append(urljoin(self.nitter_instance, src))

                tweet = Tweet(
                    id=tweet_id,
                    username=tweet_username,
                    display_name=display_name,
                    content=content,
                    url=f"https://twitter.com/{tweet_username}/status/{tweet_id}",
                    published_at=published_at,
                    likes=likes,
                    retweets=retweets,
                    replies=replies,
                    media_urls=media_urls,
                )
                tweets.append(tweet)

            except Exception as e:
                logger.warning("Failed to parse tweet", error=str(e))
                continue

        logger.info(
            "Fetched user tweets",
            username=username,
            count=len(tweets),
        )

        return tweets

    async def collect(
        self,
        influencers: list[str] | None = None,
        max_per_user: int = 5,
    ) -> list[Tweet]:
        """Collect tweets from all configured influencers.

        Args:
            influencers: List of usernames to scrape (default: configured list)
            max_per_user: Maximum tweets per user

        Returns:
            List of Tweet objects
        """
        influencers = influencers or self.influencers

        logger.info(
            "Starting Twitter collection",
            influencers=len(influencers),
            max_per_user=max_per_user,
        )

        all_tweets = []
        seen_ids = set()

        for username in influencers:
            try:
                tweets = await self.fetch_user_tweets(username)

                for tweet in tweets[:max_per_user]:
                    # Deduplicate
                    if tweet.id in seen_ids:
                        continue
                    seen_ids.add(tweet.id)

                    # Apply AI relevance filter
                    if self.filter_ai_relevant:
                        if not is_ai_relevant(tweet.content):
                            continue

                    all_tweets.append(tweet)

                # Small delay between requests
                import asyncio
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(
                    "Failed to fetch tweets from user",
                    username=username,
                    error=str(e),
                )
                continue

        logger.info(
            "Twitter collection complete",
            total_tweets=len(all_tweets),
            users_scraped=len(influencers),
        )

        return all_tweets
