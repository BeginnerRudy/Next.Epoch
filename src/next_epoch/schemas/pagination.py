"""Pagination schemas."""

from typing import Generic, TypeVar

from pydantic import Field

from next_epoch.schemas.base import BaseSchema

T = TypeVar("T")


class Pagination(BaseSchema):
    """Pagination metadata."""

    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    total_items: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, page: int, per_page: int, total_items: int) -> "Pagination":
        """Create pagination metadata from page info."""
        total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else 0
        return cls(
            page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""

    data: list[T]
    pagination: Pagination
