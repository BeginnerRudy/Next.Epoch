"""API dependencies."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from next_epoch.config import get_settings
from next_epoch.db.session import get_db_session
from next_epoch.db.repositories import (
    ContentItemRepository,
    PaperRepository,
    RepositoryRepository,
    ProcessingRunRepository,
)

settings = get_settings()


async def verify_api_key(x_api_key: str | None = Header(None)) -> str | None:
    """Verify API key from header.

    For MVP, API key is optional if not configured.
    """
    configured_key = settings.api_key
    if configured_key is None:
        # No API key configured - allow all requests (dev mode)
        return None

    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
        )

    if x_api_key != configured_key.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return x_api_key


# Dependency type aliases
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
ApiKey = Annotated[str | None, Depends(verify_api_key)]


async def get_content_repo(session: DbSession) -> ContentItemRepository:
    """Get content item repository."""
    return ContentItemRepository(session)


async def get_paper_repo(session: DbSession) -> PaperRepository:
    """Get paper repository."""
    return PaperRepository(session)


async def get_repository_repo(session: DbSession) -> RepositoryRepository:
    """Get repository repository."""
    return RepositoryRepository(session)


async def get_run_repo(session: DbSession) -> ProcessingRunRepository:
    """Get processing run repository."""
    return ProcessingRunRepository(session)


ContentRepo = Annotated[ContentItemRepository, Depends(get_content_repo)]
PaperRepo = Annotated[PaperRepository, Depends(get_paper_repo)]
RepoRepo = Annotated[RepositoryRepository, Depends(get_repository_repo)]
RunRepo = Annotated[ProcessingRunRepository, Depends(get_run_repo)]
