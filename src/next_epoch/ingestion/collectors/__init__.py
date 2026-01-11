"""Content collectors package."""

from next_epoch.ingestion.collectors.base import BaseCollector, CollectorResult
from next_epoch.ingestion.collectors.arxiv import ArxivCollector
from next_epoch.ingestion.collectors.github import GitHubTrendingCollector

__all__ = [
    "BaseCollector",
    "CollectorResult",
    "ArxivCollector",
    "GitHubTrendingCollector",
]
