"""Ingestion service that orchestrates the full ingestion pipeline."""

from dataclasses import dataclass
from datetime import datetime

import structlog

from next_epoch.config import get_settings
from next_epoch.db.models import ContentItemModel, PaperModel, RepositoryModel, ProcessingRunModel
from next_epoch.db.session import get_session_context
from next_epoch.db.repositories import (
    ContentItemRepository,
    PaperRepository,
    RepositoryRepository,
    ProcessingRunRepository,
)
from next_epoch.ingestion.collectors import ArxivCollector, GitHubTrendingCollector
from next_epoch.ingestion.normalizers import normalize_paper, normalize_repository
from next_epoch.intelligence.scorer import update_content_scores
from next_epoch.schemas.content import Paper, Repository
from next_epoch.schemas.enums import RunType, RunStatus, SourceType

logger = structlog.get_logger()
settings = get_settings()


@dataclass
class IngestionStats:
    """Statistics from an ingestion run."""
    source: str
    items_fetched: int = 0
    items_new: int = 0
    items_updated: int = 0
    items_skipped: int = 0
    items_filtered: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "source": self.source,
            "items_fetched": self.items_fetched,
            "items_new": self.items_new,
            "items_updated": self.items_updated,
            "items_skipped": self.items_skipped,
            "items_filtered": self.items_filtered,
            "error_count": len(self.errors),
        }


class IngestionService:
    """Service for ingesting content from sources."""

    def __init__(self):
        self.arxiv_collector = ArxivCollector()
        self.github_collector = GitHubTrendingCollector()

    async def close(self):
        """Close collectors."""
        await self.arxiv_collector.close()
        await self.github_collector.close()

    async def ingest_arxiv(self, max_results: int | None = None) -> IngestionStats:
        """Ingest papers from arXiv.

        Args:
            max_results: Maximum papers to fetch (default from config)

        Returns:
            IngestionStats with results
        """
        stats = IngestionStats(source="arxiv")

        try:
            # Fetch papers from arXiv
            logger.info("Starting arXiv ingestion", max_results=max_results)
            papers = await self.arxiv_collector.collect(max_results=max_results)
            stats.items_fetched = len(papers)

            async with get_session_context() as session:
                paper_repo = PaperRepository(session)
                content_repo = ContentItemRepository(session)

                for paper in papers:
                    try:
                        # Check for duplicate by canonical_ref
                        existing = await content_repo.get_by_canonical_ref(paper.canonical_ref)
                        if existing:
                            stats.items_skipped += 1
                            continue

                        # Normalize to ContentItem
                        content = normalize_paper(paper)

                        # Score the content
                        scored_content = update_content_scores(content, paper)

                        # Filter by relevance threshold
                        if scored_content.relevance_score < settings.relevance_threshold:
                            stats.items_filtered += 1
                            continue

                        # Store raw paper
                        paper_model = PaperModel(
                            id=paper.id,
                            source="arxiv",
                            external_id=paper.external_id,
                            canonical_ref=paper.canonical_ref,
                            title=paper.title,
                            authors=[{"name": a.name, "affiliation": a.affiliation} for a in paper.authors],
                            abstract=paper.abstract,
                            url=paper.url,
                            pdf_url=paper.pdf_url,
                            published_at=paper.published_at,
                            updated_at=paper.updated_at,
                            categories=paper.categories,
                            tags=paper.tags,
                        )
                        session.add(paper_model)

                        # Store content item
                        content_model = ContentItemModel(
                            id=scored_content.id,
                            type=scored_content.type.value,
                            source=scored_content.source.value,
                            canonical_ref=paper.canonical_ref,
                            title=scored_content.title,
                            summary=scored_content.summary,
                            url=scored_content.url,
                            relevance_score=scored_content.relevance_score,
                            importance_score=scored_content.importance_score,
                            novelty_score=scored_content.novelty_score,
                            frontier_score=scored_content.frontier_score,
                            score_breakdown=scored_content.score_breakdown.model_dump(mode='json') if scored_content.score_breakdown else None,
                            signals=[s.model_dump(mode='json') for s in scored_content.signals],
                            provenance=scored_content.provenance.model_dump(mode='json') if scored_content.provenance else None,
                            tags=scored_content.tags,
                            categories=scored_content.categories,
                            published_at=scored_content.published_at,
                            processed_at=scored_content.processed_at,
                            raw_content_type="paper",
                            raw_content_id=paper.id,
                        )
                        session.add(content_model)

                        stats.items_new += 1

                    except Exception as e:
                        logger.error("Failed to process paper", paper_id=paper.external_id, error=str(e))
                        stats.errors.append(f"Paper {paper.external_id}: {str(e)}")

            logger.info(
                "arXiv ingestion complete",
                fetched=stats.items_fetched,
                new=stats.items_new,
                skipped=stats.items_skipped,
                filtered=stats.items_filtered,
            )

        except Exception as e:
            logger.error("arXiv ingestion failed", error=str(e))
            stats.errors.append(str(e))

        return stats

    async def ingest_github(self) -> IngestionStats:
        """Ingest repositories from GitHub Trending.

        Returns:
            IngestionStats with results
        """
        stats = IngestionStats(source="github")

        try:
            # Fetch trending repos
            logger.info("Starting GitHub Trending ingestion")
            repos = await self.github_collector.collect()
            stats.items_fetched = len(repos)

            async with get_session_context() as session:
                repo_repo = RepositoryRepository(session)
                content_repo = ContentItemRepository(session)

                for repo in repos:
                    try:
                        # Check for duplicate
                        existing = await content_repo.get_by_canonical_ref(repo.canonical_ref)
                        if existing:
                            # Update existing with new trending info
                            stats.items_updated += 1
                            continue

                        # Normalize to ContentItem
                        content = normalize_repository(repo)

                        # Score the content
                        scored_content = update_content_scores(content, repo)

                        # Filter by relevance threshold
                        if scored_content.relevance_score < settings.relevance_threshold:
                            stats.items_filtered += 1
                            continue

                        # Store raw repository
                        repo_model = RepositoryModel(
                            id=repo.id,
                            source="github",
                            external_id=repo.external_id,
                            canonical_ref=repo.canonical_ref,
                            name=repo.name,
                            full_name=repo.full_name,
                            description=repo.description,
                            url=repo.url,
                            homepage=repo.homepage,
                            owner=repo.owner,
                            stars=repo.stars,
                            forks=repo.forks,
                            language=repo.language,
                            topics=repo.topics,
                            trending_rank=repo.trending_rank,
                            trending_since=repo.trending_since,
                        )
                        session.add(repo_model)

                        # Store content item
                        content_model = ContentItemModel(
                            id=scored_content.id,
                            type=scored_content.type.value,
                            source=scored_content.source.value,
                            canonical_ref=repo.canonical_ref,
                            title=scored_content.title,
                            summary=scored_content.summary,
                            url=scored_content.url,
                            relevance_score=scored_content.relevance_score,
                            importance_score=scored_content.importance_score,
                            novelty_score=scored_content.novelty_score,
                            frontier_score=scored_content.frontier_score,
                            score_breakdown=scored_content.score_breakdown.model_dump(mode='json') if scored_content.score_breakdown else None,
                            signals=[s.model_dump(mode='json') for s in scored_content.signals],
                            provenance=scored_content.provenance.model_dump(mode='json') if scored_content.provenance else None,
                            tags=scored_content.tags,
                            categories=scored_content.categories,
                            published_at=scored_content.published_at,
                            processed_at=scored_content.processed_at,
                            raw_content_type="repository",
                            raw_content_id=repo.id,
                        )
                        session.add(content_model)

                        stats.items_new += 1

                    except Exception as e:
                        logger.error("Failed to process repo", repo=repo.full_name, error=str(e))
                        stats.errors.append(f"Repo {repo.full_name}: {str(e)}")

            logger.info(
                "GitHub ingestion complete",
                fetched=stats.items_fetched,
                new=stats.items_new,
                updated=stats.items_updated,
                filtered=stats.items_filtered,
            )

        except Exception as e:
            logger.error("GitHub ingestion failed", error=str(e))
            stats.errors.append(str(e))

        return stats

    async def ingest_all(self) -> dict[str, IngestionStats]:
        """Ingest from all sources.

        Returns:
            Dictionary mapping source name to stats
        """
        results = {}

        # Ingest arXiv
        results["arxiv"] = await self.ingest_arxiv()

        # Ingest GitHub
        results["github"] = await self.ingest_github()

        return results


async def run_ingestion(source: SourceType | None = None) -> ProcessingRunModel:
    """Run ingestion as a tracked processing run.

    Args:
        source: Specific source to ingest, or None for all sources

    Returns:
        ProcessingRun model with results
    """
    async with get_session_context() as session:
        run_repo = ProcessingRunRepository(session)

        # Create run record
        run = await run_repo.start_run(
            run_type=RunType.INGEST,
            source=source,
        )

        try:
            service = IngestionService()

            if source == SourceType.ARXIV:
                stats = await service.ingest_arxiv()
                all_stats = {"arxiv": stats.to_dict()}
            elif source == SourceType.GITHUB:
                stats = await service.ingest_github()
                all_stats = {"github": stats.to_dict()}
            else:
                results = await service.ingest_all()
                all_stats = {k: v.to_dict() for k, v in results.items()}

            await service.close()

            # Complete run
            run = await run_repo.complete_run(run, stats=all_stats)

            logger.info("Ingestion run complete", run_id=run.id, stats=all_stats)

        except Exception as e:
            logger.error("Ingestion run failed", run_id=run.id, error=str(e))
            run = await run_repo.fail_run(run, error=str(e))

        return run
