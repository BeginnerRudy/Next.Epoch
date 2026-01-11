"""Content item repository."""

from datetime import datetime

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from next_epoch.db.models import ContentItemModel
from next_epoch.db.repositories.base import BaseRepository
from next_epoch.schemas.enums import ContentType, SourceType


class ContentItemRepository(BaseRepository[ContentItemModel]):
    """Repository for content items."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ContentItemModel)

    async def get_by_canonical_ref(self, canonical_ref: str) -> ContentItemModel | None:
        """Get content item by canonical reference (for deduplication)."""
        stmt = select(ContentItemModel).where(ContentItemModel.canonical_ref == canonical_ref)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_canonical_ref(self, canonical_ref: str) -> bool:
        """Check if content item exists by canonical reference."""
        stmt = select(func.count()).select_from(ContentItemModel).where(
            ContentItemModel.canonical_ref == canonical_ref
        )
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def list_content(
        self,
        *,
        source: SourceType | None = None,
        content_type: ContentType | None = None,
        tags: list[str] | None = None,
        category: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        sort_by: str = "published_at",
        sort_order: str = "desc",
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ContentItemModel], int]:
        """List content items with filtering and pagination."""
        # Base query
        stmt = select(ContentItemModel)
        count_stmt = select(func.count()).select_from(ContentItemModel)

        # Apply filters
        if source:
            stmt = stmt.where(ContentItemModel.source == source.value)
            count_stmt = count_stmt.where(ContentItemModel.source == source.value)

        if content_type:
            stmt = stmt.where(ContentItemModel.type == content_type.value)
            count_stmt = count_stmt.where(ContentItemModel.type == content_type.value)

        if tags:
            # Check if any of the tags are in the item's tags
            stmt = stmt.where(ContentItemModel.tags.overlap(tags))
            count_stmt = count_stmt.where(ContentItemModel.tags.overlap(tags))

        if category:
            stmt = stmt.where(ContentItemModel.categories.contains([category]))
            count_stmt = count_stmt.where(ContentItemModel.categories.contains([category]))

        if since:
            stmt = stmt.where(ContentItemModel.published_at >= since)
            count_stmt = count_stmt.where(ContentItemModel.published_at >= since)

        if until:
            stmt = stmt.where(ContentItemModel.published_at <= until)
            count_stmt = count_stmt.where(ContentItemModel.published_at <= until)

        # Apply sorting
        sort_column = getattr(ContentItemModel, sort_by, ContentItemModel.published_at)
        if sort_order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # Get total count
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def search(
        self,
        query: str,
        *,
        source: SourceType | None = None,
        content_type: ContentType | None = None,
        category: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ContentItemModel], int]:
        """Search content items by text query."""
        # Simple ILIKE search on title and summary
        search_pattern = f"%{query}%"
        stmt = select(ContentItemModel).where(
            or_(
                ContentItemModel.title.ilike(search_pattern),
                ContentItemModel.summary.ilike(search_pattern),
            )
        )
        count_stmt = select(func.count()).select_from(ContentItemModel).where(
            or_(
                ContentItemModel.title.ilike(search_pattern),
                ContentItemModel.summary.ilike(search_pattern),
            )
        )

        # Apply filters
        if source:
            stmt = stmt.where(ContentItemModel.source == source.value)
            count_stmt = count_stmt.where(ContentItemModel.source == source.value)

        if content_type:
            stmt = stmt.where(ContentItemModel.type == content_type.value)
            count_stmt = count_stmt.where(ContentItemModel.type == content_type.value)

        if category:
            stmt = stmt.where(ContentItemModel.categories.contains([category]))
            count_stmt = count_stmt.where(ContentItemModel.categories.contains([category]))

        # Order by relevance (frontier_score) then published_at
        stmt = stmt.order_by(
            ContentItemModel.frontier_score.desc().nullslast(),
            ContentItemModel.published_at.desc(),
        )

        # Get total count
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Apply pagination
        stmt = stmt.offset(offset).limit(limit)

        # Execute query
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_top_items(
        self,
        *,
        hours: int = 24,
        limit: int = 10,
        source: SourceType | None = None,
    ) -> list[ContentItemModel]:
        """Get top-ranked items from the last N hours."""
        cutoff = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Move back by hours
        from datetime import timedelta
        cutoff = cutoff - timedelta(hours=hours)

        stmt = select(ContentItemModel).where(
            ContentItemModel.published_at >= cutoff
        )

        if source:
            stmt = stmt.where(ContentItemModel.source == source.value)

        stmt = stmt.order_by(
            ContentItemModel.frontier_score.desc().nullslast(),
            ContentItemModel.importance_score.desc(),
        ).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
