"""Trend-related schemas."""

from datetime import datetime

from pydantic import Field

from next_epoch.schemas.base import BaseSchema, generate_uuid7
from next_epoch.schemas.enums import TrendMomentum


class Trend(BaseSchema):
    """Detected trend in the AI field."""

    id: str = Field(default_factory=generate_uuid7)
    name: str
    description: str | None = None
    category: str | None = None
    momentum: TrendMomentum
    confidence: float = Field(..., ge=0.0, le=1.0)
    first_detected: datetime = Field(default_factory=datetime.utcnow)
    keywords: list[str] = Field(default_factory=list)
    related_item_ids: list[str] = Field(default_factory=list)


class TrendDetails(Trend):
    """Trend with related content items."""

    # In API responses, this will include full ContentItem objects
    # For now, we just extend the base Trend
    pass
