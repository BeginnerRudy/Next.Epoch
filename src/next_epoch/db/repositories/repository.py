"""Repository repository (for GitHub repos)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from next_epoch.db.models import RepositoryModel
from next_epoch.db.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[RepositoryModel]):
    """Repository for GitHub repositories."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, RepositoryModel)

    async def get_by_full_name(self, full_name: str) -> RepositoryModel | None:
        """Get repository by full name (owner/repo)."""
        stmt = select(RepositoryModel).where(RepositoryModel.full_name == full_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_canonical_ref(self, canonical_ref: str) -> RepositoryModel | None:
        """Get repository by canonical reference."""
        stmt = select(RepositoryModel).where(RepositoryModel.canonical_ref == canonical_ref)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_full_name(self, full_name: str) -> bool:
        """Check if repository exists by full name."""
        repo = await self.get_by_full_name(full_name)
        return repo is not None
