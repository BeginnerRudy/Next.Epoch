"""Base schema utilities and types."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field
from uuid_extensions import uuid7


def generate_uuid7() -> str:
    """Generate a new UUIDv7 as a string."""
    return str(uuid7())


# Type alias for UUIDv7 fields
UUIDv7 = Annotated[str, Field(default_factory=generate_uuid7)]


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampedSchema(BaseSchema):
    """Schema with creation timestamp."""

    created_at: datetime = Field(default_factory=datetime.utcnow)


class APIErrorDetail(BaseSchema):
    """API error detail structure."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class APIError(BaseSchema):
    """API error response structure."""

    error: APIErrorDetail
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
