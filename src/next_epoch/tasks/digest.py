"""Digest generation logic."""

from datetime import datetime, timedelta
from typing import List, Dict, Any

import structlog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from next_epoch.db.models import ContentItemModel, DigestModel
from next_epoch.schemas.base import generate_uuid7
from next_epoch.schemas.enums import DigestType

logger = structlog.get_logger()


async def generate_digest(
    session: AsyncSession,
    digest_type: DigestType,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> DigestModel | None:
    """Generate a digest for the given period.

    Args:
        session: Database session
        digest_type: Type of digest (daily, weekly)
        period_start: Start of the period (defaults based on type)
        period_end: End of the period (defaults to now)

    Returns:
        Created digest model or None if no content found
    """
    now = datetime.utcnow()

    # Calculate default periods
    if digest_type == DigestType.DAILY:
        period_end = period_end or now
        period_start = period_start or (now - timedelta(days=1))
        title_date = period_start.strftime("%B %d, %Y")
        title = f"Daily AI Digest - {title_date}"
    elif digest_type == DigestType.WEEKLY:
        period_end = period_end or now
        period_start = period_start or (now - timedelta(days=7))
        start_date = period_start.strftime("%b %d")
        end_date = period_end.strftime("%b %d, %Y")
        title = f"Weekly AI Digest - {start_date} to {end_date}"
    else:
        period_end = period_end or now
        period_start = period_start or (now - timedelta(hours=6))
        title = f"AI Update - {now.strftime('%B %d, %Y')}"

    logger.info(
        "Generating digest",
        type=digest_type.value,
        period_start=period_start,
        period_end=period_end,
    )

    # Fetch top content for the period
    stmt = (
        select(ContentItemModel)
        .where(ContentItemModel.published_at >= period_start)
        .where(ContentItemModel.published_at <= period_end)
        .where(ContentItemModel.frontier_score.isnot(None))
        .order_by(ContentItemModel.frontier_score.desc())
        .limit(20)
    )

    result = await session.execute(stmt)
    items = list(result.scalars().all())

    if not items:
        logger.warning("No content found for digest period")
        return None

    # Separate by type
    papers = [i for i in items if i.type == "paper"]
    repos = [i for i in items if i.type == "repository"]

    # Build sections
    sections = []

    if papers:
        top_papers = papers[:5]
        paper_summary = f"Top {len(top_papers)} research papers from arXiv with scores ranging from {min(p.frontier_score for p in top_papers):.2f} to {max(p.frontier_score for p in top_papers):.2f}."
        sections.append({
            "name": "Top Research Papers",
            "summary": paper_summary,
            "item_ids": [p.id for p in top_papers],
        })

    if repos:
        top_repos = repos[:5]
        repo_summary = f"Top {len(top_repos)} trending GitHub repositories in AI/ML with scores ranging from {min(r.frontier_score for r in top_repos):.2f} to {max(r.frontier_score for r in top_repos):.2f}."
        sections.append({
            "name": "Trending Repositories",
            "summary": repo_summary,
            "item_ids": [r.id for r in top_repos],
        })

    # Generate highlights
    highlights = []
    if papers:
        highlights.append(f"{len(papers)} new AI research papers published")
    if repos:
        highlights.append(f"{len(repos)} trending AI repositories")

    top_item = items[0] if items else None
    if top_item:
        highlights.append(f"Top item: {top_item.title[:50]}... (score: {top_item.frontier_score:.2f})")

    # Generate executive summary
    total_papers = len(papers)
    total_repos = len(repos)

    if digest_type == DigestType.DAILY:
        summary = f"Today's AI digest features {total_papers} research papers and {total_repos} trending repositories. "
    else:
        summary = f"This week's AI digest covers {total_papers} research papers and {total_repos} trending repositories. "

    if top_item:
        summary += f"The highest-scoring item is \"{top_item.title[:60]}...\" with a frontier score of {top_item.frontier_score:.2f}."

    # Create stats
    stats = {
        "total_items": len(items),
        "papers_count": total_papers,
        "repos_count": total_repos,
        "articles_count": 0,
    }

    # Create digest
    digest = DigestModel(
        id=generate_uuid7(),
        type=digest_type.value,
        title=title,
        executive_summary=summary,
        period_start=period_start,
        period_end=period_end,
        sections=sections,
        highlights=highlights,
        stats=stats,
        generated_at=now,
        version="1.0",
    )

    session.add(digest)
    await session.flush()

    logger.info(
        "Digest generated",
        digest_id=digest.id,
        type=digest_type.value,
        item_count=len(items),
    )

    return digest


async def generate_daily_digest(session: AsyncSession) -> DigestModel | None:
    """Generate a daily digest for yesterday's content."""
    return await generate_digest(session, DigestType.DAILY)


async def generate_weekly_digest(session: AsyncSession) -> DigestModel | None:
    """Generate a weekly digest for the past week's content."""
    return await generate_digest(session, DigestType.WEEKLY)
