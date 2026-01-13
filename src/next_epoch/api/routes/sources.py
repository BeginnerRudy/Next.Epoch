"""Sources API endpoints."""

import asyncio
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, status

from next_epoch.api.deps import ApiKey, DbSession
from next_epoch.db.models import SourceConfigModel
from next_epoch.schemas.source import SourceConfig, UpdateSourceRequest
from next_epoch.schemas.enums import SourceType
from next_epoch.schemas.base import generate_uuid7
from next_epoch.tasks.ingestion import run_ingestion
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
    {
        "id": "venturebeat",
        "type": "venturebeat",
        "name": "VentureBeat AI",
        "enabled": True,
        "refresh_interval": 120,  # 2 hours for news
        "status": "active",
    },
    {
        "id": "techcrunch",
        "type": "techcrunch",
        "name": "TechCrunch AI",
        "enabled": False,  # Disabled by default, enable when needed
        "refresh_interval": 120,
        "status": "active",
    },
    {
        "id": "twitter",
        "type": "twitter",
        "name": "Twitter/X AI Influencers",
        "enabled": True,
        "refresh_interval": 60,  # 1 hour for social
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

    # Map source id to SourceType
    source_type_map = {
        "arxiv": SourceType.ARXIV,
        "github": SourceType.GITHUB,
        "venturebeat": SourceType.VENTUREBEAT,
        "techcrunch": SourceType.TECHCRUNCH,
        "twitter": SourceType.TWITTER,
    }
    source_type = source_type_map.get(id)
    if not source_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown source type: {id}",
        )

    job_id = generate_uuid7()

    # Run ingestion in background task
    asyncio.create_task(run_ingestion(source_type))

    return {
        "message": f"Refresh triggered for source {id}",
        "job_id": job_id,
    }
