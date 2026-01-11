"""Processing runs API endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from next_epoch.api.deps import ApiKey, RunRepo
from next_epoch.db.models import ProcessingRunModel
from next_epoch.schemas.run import ProcessingRun, CreateRunRequest
from next_epoch.schemas.enums import RunType, RunStatus, SourceType
from next_epoch.schemas.pagination import Pagination, PaginatedResponse

router = APIRouter()


def model_to_schema(model: ProcessingRunModel) -> ProcessingRun:
    """Convert database model to Pydantic schema."""
    return ProcessingRun(
        id=model.id,
        type=RunType(model.type),
        status=RunStatus(model.status),
        source=SourceType(model.source) if model.source else None,
        started_at=model.started_at,
        finished_at=model.finished_at,
        stats=model.stats,
        error=model.error,
    )


@router.get("/runs")
async def list_runs(
    _api_key: ApiKey,
    repo: RunRepo,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    type: RunType | None = None,
    status: RunStatus | None = None,
    source: SourceType | None = None,
) -> PaginatedResponse[ProcessingRun]:
    """List processing runs with filtering."""
    offset = (page - 1) * per_page

    runs, total = await repo.list_runs(
        run_type=type,
        status=status,
        source=source,
        offset=offset,
        limit=per_page,
    )

    run_schemas = [model_to_schema(r) for r in runs]

    return PaginatedResponse(
        data=run_schemas,
        pagination=Pagination.create(page=page, per_page=per_page, total_items=total),
    )


@router.get("/runs/{id}")
async def get_run(
    id: str,
    _api_key: ApiKey,
    repo: RunRepo,
) -> ProcessingRun:
    """Get a processing run by ID."""
    run = await repo.get_by_id(id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processing run {id} not found",
        )
    return model_to_schema(run)


@router.post("/runs", status_code=status.HTTP_202_ACCEPTED)
async def create_run(
    request: CreateRunRequest,
    _api_key: ApiKey,
    repo: RunRepo,
) -> ProcessingRun:
    """Create a new processing run."""
    run = await repo.start_run(
        run_type=request.type,
        source=request.source,
    )

    # TODO: Queue the actual processing task based on run type

    return model_to_schema(run)
