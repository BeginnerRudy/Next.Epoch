"""Sources API endpoints."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status

from next_epoch.api.deps import ApiKey, DbSession
from next_epoch.db.models import SourceConfigModel
from next_epoch.schemas.source import SourceConfig, UpdateSourceRequest
from next_epoch.schemas.enums import SourceType
from next_epoch.schemas.base import generate_uuid7
from sqlalchemy import select

router = APIRouter()


# Default source configurations
DEFAULT_SOURCES = [
    {
        "id": "arxiv",
        "type": "arxiv",
        "name": "arXiv",
        "enabled": True,
        "refresh_interval": 60,
        "status": "active",
    },
    {
        "id": "github",
        "type": "github",
        "name": "GitHub Trending",
        "enabled": True,
        "refresh_interval": 60,
        "status": "active",
    },
]


def model_to_schema(model: SourceConfigModel) -> SourceConfig:
    """Convert database model to Pydantic schema."""
    return SourceConfig(
        id=model.id,
        type=SourceType(model.type),
        name=model.name,
        enabled=model.enabled,
        refresh_interval=model.refresh_interval,
        last_fetched=model.last_fetched,
        status=model.status,
        error_count=model.error_count,
    )


@router.get("/sources")
async def list_sources(
    _api_key: ApiKey,
    session: DbSession,
) -> list[SourceConfig]:
    """List all configured sources."""
    stmt = select(SourceConfigModel)
    result = await session.execute(stmt)
    models = list(result.scalars().all())

    # If no sources in DB, return defaults
    if not models:
        return [SourceConfig(**s) for s in DEFAULT_SOURCES]

    return [model_to_schema(m) for m in models]


@router.get("/sources/{id}")
async def get_source(
    id: str,
    _api_key: ApiKey,
    session: DbSession,
) -> SourceConfig:
    """Get source configuration by ID."""
    model = await session.get(SourceConfigModel, id)

    # Check defaults if not in DB
    if not model:
        for default in DEFAULT_SOURCES:
            if default["id"] == id:
                return SourceConfig(**default)

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {id} not found",
        )

    return model_to_schema(model)


@router.patch("/sources/{id}")
async def update_source(
    id: str,
    request: UpdateSourceRequest,
    _api_key: ApiKey,
    session: DbSession,
) -> SourceConfig:
    """Update source configuration."""
    model = await session.get(SourceConfigModel, id)

    # Create from defaults if not in DB
    if not model:
        default = None
        for d in DEFAULT_SOURCES:
            if d["id"] == id:
                default = d
                break

        if not default:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source {id} not found",
            )

        model = SourceConfigModel(**default)
        session.add(model)

    # Apply updates
    if request.enabled is not None:
        model.enabled = request.enabled
    if request.refresh_interval is not None:
        model.refresh_interval = request.refresh_interval

    model.updated_at = datetime.utcnow()
    await session.flush()

    return model_to_schema(model)


@router.post("/sources/{id}/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_source(
    id: str,
    _api_key: ApiKey,
    session: DbSession,
) -> dict:
    """Trigger a source refresh manually."""
    # Verify source exists
    model = await session.get(SourceConfigModel, id)
    if not model:
        # Check defaults
        found = any(d["id"] == id for d in DEFAULT_SOURCES)
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source {id} not found",
            )

    # TODO: Queue actual refresh task
    job_id = generate_uuid7()

    return {
        "message": f"Refresh triggered for source {id}",
        "job_id": job_id,
    }
