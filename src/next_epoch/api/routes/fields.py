"""Fields/taxonomy API endpoints."""

from fastapi import APIRouter, HTTPException, status

from next_epoch.api.deps import ApiKey, DbSession
from next_epoch.db.models import TaxonomyFieldModel
from next_epoch.schemas.field import TaxonomyField
from next_epoch.schemas.enums import FieldStatus
from sqlalchemy import select

router = APIRouter()


# Default fields for MVP
DEFAULT_FIELDS = [
    {"id": "llm", "name": "Large Language Models", "description": "LLMs, transformers, and language modeling"},
    {"id": "agents", "name": "AI Agents", "description": "Autonomous agents, tool use, and agentic systems"},
    {"id": "vision", "name": "Computer Vision", "description": "Image recognition, generation, and visual understanding"},
    {"id": "robotics", "name": "Robotics", "description": "Embodied AI, manipulation, and autonomous systems"},
    {"id": "rl", "name": "Reinforcement Learning", "description": "RL algorithms, environments, and applications"},
    {"id": "safety", "name": "AI Safety", "description": "Alignment, interpretability, and responsible AI"},
    {"id": "multimodal", "name": "Multimodal AI", "description": "Vision-language models and cross-modal learning"},
    {"id": "diffusion", "name": "Diffusion Models", "description": "Generative models for images, video, and more"},
    {"id": "retrieval", "name": "Retrieval & RAG", "description": "Retrieval-augmented generation and knowledge bases"},
    {"id": "efficiency", "name": "Efficient AI", "description": "Quantization, distillation, and inference optimization"},
]


def model_to_schema(model: TaxonomyFieldModel) -> TaxonomyField:
    """Convert database model to Pydantic schema."""
    return TaxonomyField(
        id=model.id,
        name=model.name,
        description=model.description,
        parent_id=model.parent_id,
        aliases=model.aliases or [],
        status=FieldStatus(model.status),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@router.get("/fields")
async def list_fields(
    _api_key: ApiKey,
    session: DbSession,
) -> list[TaxonomyField]:
    """List all taxonomy fields."""
    stmt = select(TaxonomyFieldModel).where(TaxonomyFieldModel.status == "active")
    result = await session.execute(stmt)
    models = list(result.scalars().all())

    # If no fields in DB, return defaults
    if not models:
        from datetime import datetime
        now = datetime.utcnow()
        return [
            TaxonomyField(
                id=f["id"],
                name=f["name"],
                description=f.get("description"),
                status=FieldStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            for f in DEFAULT_FIELDS
        ]

    return [model_to_schema(m) for m in models]


@router.get("/fields/{id}")
async def get_field(
    id: str,
    _api_key: ApiKey,
    session: DbSession,
) -> TaxonomyField:
    """Get a field by ID."""
    model = await session.get(TaxonomyFieldModel, id)

    # Check defaults if not in DB
    if not model:
        for default in DEFAULT_FIELDS:
            if default["id"] == id:
                from datetime import datetime
                now = datetime.utcnow()
                return TaxonomyField(
                    id=default["id"],
                    name=default["name"],
                    description=default.get("description"),
                    status=FieldStatus.ACTIVE,
                    created_at=now,
                    updated_at=now,
                )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field {id} not found",
        )

    return model_to_schema(model)
