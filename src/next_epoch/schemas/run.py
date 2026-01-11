"""Processing run schemas."""

from datetime import datetime
from typing import Any

from pydantic import Field

from next_epoch.schemas.base import BaseSchema, generate_uuid7
from next_epoch.schemas.enums import RunStatus, RunType, SourceType


class ProcessingRun(BaseSchema):
    """Auditable processing run record."""

    id: str = Field(default_factory=generate_uuid7)
    type: RunType
    status: RunStatus = RunStatus.PENDING
    source: SourceType | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: datetime | None = None
    stats: dict[str, Any] | None = Field(
        None, description="Run statistics (e.g., items_fetched, items_created, llm_calls)"
    )
    error: str | None = None


class CreateRunRequest(BaseSchema):
    """Request to create a processing run."""

    type: RunType
    source: SourceType | None = None
    parameters: dict[str, Any] | None = None
