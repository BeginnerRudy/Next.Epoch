"""Digest-related schemas."""

from datetime import datetime

from pydantic import Field as PydanticField

from next_epoch.schemas.base import BaseSchema, generate_uuid7
from next_epoch.schemas.enums import DigestType


class DigestStats(BaseSchema):
    """Statistics for a digest."""

    total_items: int = 0
    papers_count: int = 0
    articles_count: int = 0
    repos_count: int = 0


class DigestSection(BaseSchema):
    """Section within a digest."""

    name: str
    summary: str
    item_ids: list[str] = PydanticField(
        default_factory=list, description="IDs of content items in this section"
    )


class Digest(BaseSchema):
    """Curated content collection for a time period."""

    id: str = PydanticField(default_factory=generate_uuid7)
    type: DigestType
    title: str
    executive_summary: str = PydanticField(..., description="TL;DR summary")
    period_start: datetime
    period_end: datetime
    sections: list[DigestSection] = PydanticField(default_factory=list)
    highlights: list[str] = PydanticField(default_factory=list, description="Key highlights")
    stats: DigestStats = PydanticField(default_factory=DigestStats)
    generated_at: datetime = PydanticField(default_factory=datetime.utcnow)
    version: str = "1.0"


class CreateDigestRequest(BaseSchema):
    """Request to create a new digest."""

    type: DigestType
    period_start: datetime | None = None
    period_end: datetime | None = None
    sources: list[str] | None = None
    tags: list[str] | None = None


class DigestJob(BaseSchema):
    """Digest generation job status."""

    job_id: str
    digest_id: str | None = None
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
