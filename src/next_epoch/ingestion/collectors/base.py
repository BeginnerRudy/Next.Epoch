"""Base collector interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

import structlog

T = TypeVar("T")
logger = structlog.get_logger()


@dataclass
class CollectorResult:
    """Result of a collection operation."""

    items_fetched: int = 0
    items_new: int = 0
    items_updated: int = 0
    items_skipped: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_stats(self) -> dict:
        """Convert to stats dict for processing run."""
        return {
            "items_fetched": self.items_fetched,
            "items_new": self.items_new,
            "items_updated": self.items_updated,
            "items_skipped": self.items_skipped,
            "error_count": len(self.errors),
        }


class BaseCollector(ABC, Generic[T]):
    """Base class for content collectors."""

    source_name: str = "unknown"

    @abstractmethod
    async def collect(self, **kwargs) -> list[T]:
        """Collect items from the source.

        Returns a list of raw items (Paper, Repository, etc.)
        """
        ...

    @abstractmethod
    async def fetch_page(self, **kwargs) -> list[T]:
        """Fetch a single page of items."""
        ...

    async def run(self, **kwargs) -> CollectorResult:
        """Run the collector and return statistics."""
        result = CollectorResult()
        try:
            items = await self.collect(**kwargs)
            result.items_fetched = len(items)
            logger.info(
                "collection_complete",
                source=self.source_name,
                items_fetched=result.items_fetched,
            )
        except Exception as e:
            result.errors.append(str(e))
            logger.error(
                "collection_failed",
                source=self.source_name,
                error=str(e),
            )
        return result
