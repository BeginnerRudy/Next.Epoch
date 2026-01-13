"""Content collectors package."""

from next_epoch.ingestion.collectors.base import BaseCollector, CollectorResult
from next_epoch.ingestion.collectors.arxiv import ArxivCollector
from next_epoch.ingestion.collectors.github import GitHubTrendingCollector
from next_epoch.ingestion.collectors.news import AINewsCollector
from next_epoch.ingestion.collectors.twitter import TwitterCollector

__all__ = [
    "BaseCollector",
    "CollectorResult",
    "ArxivCollector",
    "GitHubTrendingCollector",
    "AINewsCollector",
    "TwitterCollector",
]
