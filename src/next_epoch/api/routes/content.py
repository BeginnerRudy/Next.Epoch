"""Content API endpoints."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from next_epoch.api.deps import ApiKey, ContentRepo, DbSession
from next_epoch.db.models import ContentItemModel, FeedbackModel
from next_epoch.schemas.content import ContentItem, ScoreBreakdown, Signal, ContentProvenance
from next_epoch.schemas.enums import ContentType, SourceType, FeedbackKind
from next_epoch.schemas.feedback import CreateFeedbackRequest, Feedback
from next_epoch.schemas.pagination import Pagination, PaginatedResponse
from next_epoch.schemas.base import generate_uuid7

router = APIRouter()


def model_to_schema(model: ContentItemModel) -> ContentItem:
    """Convert database model to Pydantic schema."""
    # Parse score breakdown if present
    score_breakdown = None
    if model.score_breakdown:
        score_breakdown = ScoreBreakdown(**model.score_breakdown)

    # Parse signals if present
    signals = []
    if model.signals:
        signals = [Signal(**s) for s in model.signals]

    # Parse provenance if present
    provenance = None
    if model.provenance:
        provenance = ContentProvenance(**model.provenance)

    return ContentItem(
        id=model.id,
        type=ContentType(model.type),
        source=SourceType(model.source),
        title=model.title,
        summary=model.summary,
        url=model.url,
        relevance_score=model.relevance_score or 0.0,
        importance_score=model.importance_score or 0.0,
        novelty_score=model.novelty_score,
        frontier_score=model.frontier_score,
        score_breakdown=score_breakdown,
        tags=model.tags or [],
        categories=model.categories or [],
        published_at=model.published_at,
        processed_at=model.processed_at,
        signals=signals,
        provenance=provenance,
        raw_content_type=model.raw_content_type,
        raw_content_id=model.raw_content_id,
    )


@router.get("/content")
async def list_content(
    _api_key: ApiKey,
    repo: ContentRepo,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    source: SourceType | None = None,
    type: ContentType | None = None,
    tags: str | None = None,
    category: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    sort: str = "published_at",
    order: str = "desc",
) -> PaginatedResponse[ContentItem]:
    """List all content with filtering and pagination."""
    # Parse tags if provided
    tag_list = tags.split(",") if tags else None

    # Calculate offset
    offset = (page - 1) * per_page

    # Fetch content
    items, total = await repo.list_content(
        source=source,
        content_type=type,
        tags=tag_list,
        category=category,
        since=since,
        until=until,
        sort_by=sort,
        sort_order=order,
        offset=offset,
        limit=per_page,
    )

    # Convert to schemas
    content_items = [model_to_schema(item) for item in items]

    return PaginatedResponse(
        data=content_items,
        pagination=Pagination.create(page=page, per_page=per_page, total_items=total),
    )


@router.get("/content/search")
async def search_content(
    _api_key: ApiKey,
    repo: ContentRepo,
    q: Annotated[str, Query(min_length=2, max_length=200)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    source: SourceType | None = None,
    type: ContentType | None = None,
    category: str | None = None,
) -> PaginatedResponse[ContentItem]:
    """Search content by text query."""
    offset = (page - 1) * per_page

    items, total = await repo.search(
        query=q,
        source=source,
        content_type=type,
        category=category,
        offset=offset,
        limit=per_page,
    )

    content_items = [model_to_schema(item) for item in items]

    return PaginatedResponse(
        data=content_items,
        pagination=Pagination.create(page=page, per_page=per_page, total_items=total),
    )


@router.get("/content/{id}")
async def get_content(
    id: str,
    _api_key: ApiKey,
    repo: ContentRepo,
) -> ContentItem:
    """Get a single content item by ID."""
    item = await repo.get_by_id(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content item {id} not found",
        )
    return model_to_schema(item)


@router.post("/content/{id}/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(
    id: str,
    request: CreateFeedbackRequest,
    _api_key: ApiKey,
    repo: ContentRepo,
    session: DbSession,
) -> Feedback:
    """Submit feedback for a content item."""
    # Verify content exists
    item = await repo.get_by_id(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content item {id} not found",
        )

    # Create feedback
    feedback = FeedbackModel(
        id=generate_uuid7(),
        content_id=id,
        kind=request.kind.value,
        rating=request.rating,
        comment=request.comment,
        actor=None,  # Would be set from API key info
        created_at=datetime.utcnow(),
    )

    session.add(feedback)
    await session.flush()

    return Feedback(
        id=feedback.id,
        content_id=feedback.content_id,
        kind=FeedbackKind(feedback.kind),
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at,
        actor=feedback.actor,
    )
