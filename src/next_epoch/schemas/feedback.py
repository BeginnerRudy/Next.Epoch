"""Feedback schemas for evaluation loop."""

from datetime import datetime

from pydantic import Field

from next_epoch.schemas.base import BaseSchema, generate_uuid7
from next_epoch.schemas.enums import FeedbackKind


class CreateFeedbackRequest(BaseSchema):
    """Request to create feedback on content."""

    kind: FeedbackKind
    rating: int = Field(..., ge=1, le=5, description="Rating on 1-5 scale")
    comment: str | None = None


class Feedback(BaseSchema):
    """Recorded feedback for evaluation."""

    id: str = Field(default_factory=generate_uuid7)
    content_id: str
    kind: FeedbackKind
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    actor: str | None = Field(None, description="API key id, user id, or 'anonymous'")
