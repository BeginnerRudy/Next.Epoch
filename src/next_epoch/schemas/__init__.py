"""Pydantic schemas for Next.Epoch domain models."""

from next_epoch.schemas.base import UUIDv7
from next_epoch.schemas.content import (
    ContentItem,
    ContentProvenance,
    FieldRef,
    Paper,
    Repository,
    ScoreBreakdown,
    Signal,
)
from next_epoch.schemas.digest import Digest, DigestSection, DigestStats
from next_epoch.schemas.enums import (
    AnnouncementType,
    ContentType,
    DigestType,
    FeedbackKind,
    FieldStatus,
    RunStatus,
    RunType,
    SourceType,
    TrendMomentum,
)
from next_epoch.schemas.feedback import CreateFeedbackRequest, Feedback
from next_epoch.schemas.field import TaxonomyField
from next_epoch.schemas.pagination import Pagination, PaginatedResponse
from next_epoch.schemas.run import CreateRunRequest, ProcessingRun
from next_epoch.schemas.source import SourceConfig, UpdateSourceRequest
from next_epoch.schemas.trend import Trend, TrendDetails

__all__ = [
    # Base
    "UUIDv7",
    # Enums
    "SourceType",
    "ContentType",
    "DigestType",
    "AnnouncementType",
    "TrendMomentum",
    "FieldStatus",
    "RunType",
    "RunStatus",
    "FeedbackKind",
    # Content
    "ContentItem",
    "ContentProvenance",
    "Paper",
    "Repository",
    "ScoreBreakdown",
    "Signal",
    # Field
    "TaxonomyField",
    "FieldRef",
    # Digest
    "Digest",
    "DigestSection",
    "DigestStats",
    # Trend
    "Trend",
    "TrendDetails",
    # Run
    "ProcessingRun",
    "CreateRunRequest",
    # Source
    "SourceConfig",
    "UpdateSourceRequest",
    # Feedback
    "Feedback",
    "CreateFeedbackRequest",
    # Pagination
    "Pagination",
    "PaginatedResponse",
]
