"""Base repository with common CRUD operations."""

from typing import Generic, TypeVar
from uuid_extensions import uuid7

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from next_epoch.db.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Base repository with common database operations."""

    def __init__(self, session: AsyncSession, model_class: type[ModelT]):
        self.session = session
        self.model_class = model_class

    @staticmethod
    def generate_id() -> str:
        """Generate a new UUIDv7."""
        return str(uuid7())

    async def get_by_id(self, id: str) -> ModelT | None:
        """Get a record by ID."""
        return await self.session.get(self.model_class, id)

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ModelT]:
        """Get all records with pagination."""
        stmt = select(self.model_class).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Get total count of records."""
        stmt = select(func.count()).select_from(self.model_class)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def create(self, entity: ModelT) -> ModelT:
        """Create a new record."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        """Update an existing record."""
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Delete a record."""
        await self.session.delete(entity)
        await self.session.flush()

    async def delete_by_id(self, id: str) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        entity = await self.get_by_id(id)
        if entity:
            await self.delete(entity)
            return True
        return False
