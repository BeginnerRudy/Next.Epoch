"""Content-related schemas."""

from datetime import datetime

from pydantic import Field as PydanticField

from next_epoch.schemas.base import BaseSchema, generate_uuid7
from next_epoch.schemas.enums import ContentType, SourceType


class Author(BaseSchema):
    """Author information."""

    name: str
    affiliation: str | None = None
    email: str | None = None
    url: str | None = None


class Signal(BaseSchema):
    """Evidence signal used for scoring and explainability."""

    key: str = PydanticField(..., description="Signal identifier (e.g., 'has_code', 'stars_velocity')")
    value: str | int | float | bool = PydanticField(..., description="Signal value")
    weight: float | None = PydanticField(None, description="Weight used in scoring, if applicable")
    source: str | None = PydanticField(None, description="Where the signal came from")


class ScoreBreakdown(BaseSchema):
    """Score breakdown with explanation."""

    relevance: float = PydanticField(..., ge=0.0, le=1.0)
    importance: float = PydanticField(..., ge=0.0, le=1.0)
    novelty: float | None = PydanticField(None, ge=0.0, le=1.0)
    frontier: float | None = PydanticField(None, ge=0.0, le=1.0)
    explanation: str | None = PydanticField(None, description="Human-readable scoring justification")


class ContentProvenance(BaseSchema):
    """Provenance information for content traceability."""

    fetched_at: datetime
    fetched_from: str = PydanticField(..., description="URL or source endpoint")
    parser: str = PydanticField(..., description="Parser/normalizer name")
    parser_version: str
    content_hash: str | None = PydanticField(None, description="Hash of normalized text")
    language: str | None = None


class Paper(BaseSchema):
    """Research paper (primarily from arXiv)."""

    id: str = PydanticField(default_factory=generate_uuid7)
    source: SourceType = SourceType.ARXIV
    external_id: str = PydanticField(..., description="ID from source (e.g., arXiv ID '2401.12345')")
    canonical_ref: str = PydanticField(..., description="Stable dedupe key (e.g., 'arxiv:2401.12345')")
    title: str
    authors: list[Author]
    abstract: str
    url: str
    pdf_url: str | None = None
    published_at: datetime
    updated_at: datetime | None = None
    categories: list[str] = PydanticField(default_factory=list, description="arXiv categories")
    tags: list[str] = PydanticField(default_factory=list, description="Auto-generated topic tags")
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)


class Repository(BaseSchema):
    """GitHub repository."""

    id: str = PydanticField(default_factory=generate_uuid7)
    source: SourceType = SourceType.GITHUB
    external_id: str = PydanticField(..., description="GitHub repo ID")
    canonical_ref: str = PydanticField(..., description="Stable dedupe key (e.g., 'github:owner/repo')")
    name: str
    full_name: str = PydanticField(..., description="owner/repo")
    description: str | None = None
    url: str
    homepage: str | None = None
    owner: str
    stars: int = 0
    forks: int = 0
    language: str | None = None
    topics: list[str] = PydanticField(default_factory=list, description="GitHub topics")
    trending_rank: int | None = None
    trending_since: datetime | None = None
    repo_created_at: datetime | None = None
    pushed_at: datetime | None = None
    ingested_at: datetime = PydanticField(default_factory=datetime.utcnow)


class Article(BaseSchema):
    """News article from AI news sites."""

    id: str = PydanticField(default_factory=generate_uuid7)
    source: SourceType
    external_id: str | None = None
    canonical_ref: str
    title: str
    author: str | None = None
    content: str
    excerpt: str
    url: str
    image_url: str | None = None
    published_at: datetime
    tags: list[str] = PydanticField(default_factory=list)
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)


class Application(BaseSchema):
    """AI-powered product or tool (apps, plugins, services)."""

    id: str = PydanticField(default_factory=generate_uuid7)
    source: SourceType
    external_id: str | None = None
    canonical_ref: str = PydanticField(..., description="Stable dedupe key (e.g., 'app:company/product')")
    name: str = PydanticField(..., description="Product/tool name")
    description: str
    url: str
    company: str | None = PydanticField(None, description="Company or creator name")
    category: str | None = PydanticField(None, description="App category (chatbot, automation, analytics, etc.)")
    use_case: str | None = PydanticField(None, description="Target use case (enterprise, consumer, developer)")
    published_at: datetime
    image_url: str | None = None
    tags: list[str] = PydanticField(default_factory=list)
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)


class Tweet(BaseSchema):
    """Tweet from Twitter/X."""

    id: str = PydanticField(default_factory=generate_uuid7)
    source: SourceType = SourceType.TWITTER
    external_id: str = PydanticField(..., description="Twitter tweet ID")
    canonical_ref: str = PydanticField(..., description="Stable dedupe key (e.g., 'twitter:username/tweet_id')")
    username: str = PydanticField(..., description="Twitter username without @")
    display_name: str = PydanticField(..., description="User display name")
    content: str = PydanticField(..., description="Tweet text content")
    url: str
    published_at: datetime
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    media_urls: list[str] = PydanticField(default_factory=list, description="URLs to attached media")
    is_thread: bool = PydanticField(False, description="Whether this is part of a thread")
    tags: list[str] = PydanticField(default_factory=list)
    created_at: datetime = PydanticField(default_factory=datetime.utcnow)


class FieldRef(BaseSchema):
    """Reference to a field with confidence score."""

    field_id: str
    confidence: float = PydanticField(..., ge=0.0, le=1.0)


class ContentItem(BaseSchema):
    """Unified content wrapper for any content type."""

    id: str = PydanticField(default_factory=generate_uuid7)
    type: ContentType
    source: SourceType
    title: str
    summary: str | None = None
    url: str
    relevance_score: float = PydanticField(0.0, ge=0.0, le=1.0)
    importance_score: float = PydanticField(0.0, ge=0.0, le=1.0)
    novelty_score: float | None = PydanticField(None, ge=0.0, le=1.0)
    frontier_score: float | None = PydanticField(None, ge=0.0, le=1.0)
    score_breakdown: ScoreBreakdown | None = None
    tags: list[str] = PydanticField(default_factory=list)
    categories: list[str] = PydanticField(default_factory=list, description="Broad categories / fields")
    published_at: datetime
    processed_at: datetime = PydanticField(default_factory=datetime.utcnow)
    fields: list[FieldRef] = PydanticField(default_factory=list)
    signals: list[Signal] = PydanticField(default_factory=list)
    provenance: ContentProvenance | None = None
    # Raw content reference - stored as JSON in DB
    raw_content_type: str | None = PydanticField(None, description="Type of raw content (paper, repository, etc.)")
    raw_content_id: str | None = PydanticField(None, description="ID of raw content record")
    # Full raw content details (only included in detail view)
    raw_content: dict | None = PydanticField(None, description="Full raw content details (abstract, authors, stars, etc.)")
