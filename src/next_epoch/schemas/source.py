"""Source configuration schemas."""

from datetime import datetime

from pydantic import Field

from next_epoch.schemas.base import BaseSchema
from next_epoch.schemas.enums import SourceType


class SourceConfig(BaseSchema):
    """Content source configuration."""

    id: str
    type: SourceType
    name: str
    enabled: bool = True
    refresh_interval: int = Field(60, description="Minutes between refreshes")
    last_fetched: datetime | None = None
    status: str = "active"  # active, error, disabled
    error_count: int = 0


class UpdateSourceRequest(BaseSchema):
    """Request to update source configuration."""

    enabled: bool | None = None
    refresh_interval: int | None = Field(None, ge=5, le=1440)
