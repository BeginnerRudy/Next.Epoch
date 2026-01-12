"""Digest API endpoints."""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from next_epoch.api.deps import ApiKey, DbSession
from next_epoch.db.models import DigestModel
from next_epoch.schemas.digest import Digest, DigestSection, DigestStats, CreateDigestRequest, DigestJob
from next_epoch.schemas.enums import DigestType
from next_epoch.schemas.pagination import Pagination, PaginatedResponse
from next_epoch.schemas.base import generate_uuid7
from next_epoch.tasks.digest import generate_digest
from sqlalchemy import select, func

router = APIRouter()


def model_to_schema(model: DigestModel) -> Digest:
    """Convert database model to Pydantic schema."""
    sections = []
    if model.sections:
        for s in model.sections:
            sections.append(DigestSection(**s))

    stats = DigestStats()
    if model.stats:
        stats = DigestStats(**model.stats)

    return Digest(
        id=model.id,
        type=DigestType(model.type),
        title=model.title,
        executive_summary=model.executive_summary,
        period_start=model.period_start,
        period_end=model.period_end,
        sections=sections,
        highlights=model.highlights or [],
        stats=stats,
        generated_at=model.generated_at,
        version=model.version,
    )


@router.get("/digests")
async def list_digests(
    _api_key: ApiKey,
    session: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    type: DigestType | None = None,
) -> PaginatedResponse[Digest]:
    """List all digests with pagination."""
    offset = (page - 1) * per_page

    # Build query
    stmt = select(DigestModel)
    count_stmt = select(func.count()).select_from(DigestModel)

    if type:
        stmt = stmt.where(DigestModel.type == type.value)
        count_stmt = count_stmt.where(DigestModel.type == type.value)

    stmt = stmt.order_by(DigestModel.generated_at.desc())
    stmt = stmt.offset(offset).limit(per_page)

    # Execute
    result = await session.execute(stmt)
    models = list(result.scalars().all())

    count_result = await session.execute(count_stmt)
    total = count_result.scalar() or 0

    digests = [model_to_schema(m) for m in models]

    return PaginatedResponse(
        data=digests,
        pagination=Pagination.create(page=page, per_page=per_page, total_items=total),
    )


@router.get("/digests/latest")
async def get_latest_digest(
    _api_key: ApiKey,
    session: DbSession,
    type: DigestType,
) -> Digest:
    """Get the most recent digest of a given type."""
    stmt = (
        select(DigestModel)
        .where(DigestModel.type == type.value)
        .order_by(DigestModel.generated_at.desc())
        .limit(1)
    )

    result = await session.execute(stmt)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No digest found for type {type.value}",
        )

    return model_to_schema(model)


@router.get("/digests/{id}")
async def get_digest(
    id: str,
    _api_key: ApiKey,
    session: DbSession,
) -> Digest:
    """Get a digest by ID."""
    model = await session.get(DigestModel, id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Digest {id} not found",
        )
    return model_to_schema(model)


@router.post("/digests", status_code=status.HTTP_201_CREATED)
async def create_digest_endpoint(
    request: CreateDigestRequest,
    _api_key: ApiKey,
    session: DbSession,
) -> Digest:
    """Generate a new digest synchronously."""
    now = datetime.utcnow()

    # Calculate default period based on digest type
    if request.type == DigestType.DAILY:
        period_start = request.period_start or (now - timedelta(days=1))
        period_end = request.period_end or now
    elif request.type == DigestType.WEEKLY:
        period_start = request.period_start or (now - timedelta(days=7))
        period_end = request.period_end or now
    else:
        period_start = request.period_start or (now - timedelta(hours=6))
        period_end = request.period_end or now

    # Generate the digest
    digest = await generate_digest(
        session=session,
        digest_type=request.type,
        period_start=period_start,
        period_end=period_end,
    )

    if not digest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No content found for the specified period",
        )

    await session.commit()
    return model_to_schema(digest)
