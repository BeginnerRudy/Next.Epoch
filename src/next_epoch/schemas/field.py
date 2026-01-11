"""Field/taxonomy schemas."""

from datetime import datetime

from pydantic import Field as PydanticField

from next_epoch.schemas.base import BaseSchema
from next_epoch.schemas.enums import FieldStatus


class TaxonomyField(BaseSchema):
    """Field in the AI taxonomy."""

    id: str = PydanticField(..., description="Stable field ID (e.g., 'agents', 'llm')")
    name: str = PydanticField(..., description="Display name")
    description: str | None = None
    parent_id: str | None = PydanticField(None, description="Parent field ID for hierarchy")
    aliases: list[str] = PydanticField(default_factory=list, description="Alternate names")
    status: FieldStatus = FieldStatus.ACTIVE
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)
    updated_at: datetime = PydanticField(default_factory=datetime.utcnow)
