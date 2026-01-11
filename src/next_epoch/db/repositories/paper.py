"""Paper repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from next_epoch.db.models import PaperModel
from next_epoch.db.repositories.base import BaseRepository


class PaperRepository(BaseRepository[PaperModel]):
    """Repository for research papers."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PaperModel)

    async def get_by_external_id(self, external_id: str) -> PaperModel | None:
        """Get paper by external ID (e.g., arXiv ID)."""
        stmt = select(PaperModel).where(PaperModel.external_id == external_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_canonical_ref(self, canonical_ref: str) -> PaperModel | None:
        """Get paper by canonical reference."""
        stmt = select(PaperModel).where(PaperModel.canonical_ref == canonical_ref)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_external_id(self, external_id: str) -> bool:
        """Check if paper exists by external ID."""
        paper = await self.get_by_external_id(external_id)
        return paper is not None
