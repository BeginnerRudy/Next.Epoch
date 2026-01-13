"""SQLAlchemy database models for Next.Epoch."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    type_annotation_map = {
        dict[str, Any]: JSONB,
        list[str]: ARRAY(String),
    }


class ContentItemModel(Base):
    """Unified content item table."""

    __tablename__ = "content_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    canonical_ref: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # Scores
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    novelty_score: Mapped[float | None] = mapped_column(Float)
    frontier_score: Mapped[float | None] = mapped_column(Float, index=True)

    # Score breakdown and signals stored as JSONB
    score_breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    signals: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    provenance: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # Taxonomy
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    fields: Mapped[dict[str, Any] | None] = mapped_column(JSONB)  # List of FieldRef

    # Timestamps
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Raw content reference
    raw_content_type: Mapped[str | None] = mapped_column(String(20))
    raw_content_id: Mapped[str | None] = mapped_column(String(36))

    # Relationships
    feedbacks: Mapped[list["FeedbackModel"]] = relationship(back_populates="content_item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_content_items_published_at_desc", published_at.desc()),
        Index("ix_content_items_frontier_score_desc", frontier_score.desc().nullslast()),
        Index("ix_content_items_tags", tags, postgresql_using="gin"),
    )


class PaperModel(Base):
    """Research paper table (raw content from arXiv)."""

    __tablename__ = "papers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(20), default="arxiv")
    external_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    canonical_ref: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)  # List of Author dicts
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    pdf_url: Mapped[str | None] = mapped_column(String(2048))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class RepositoryModel(Base):
    """GitHub repository table (raw content)."""

    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(20), default="github")
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    canonical_ref: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    homepage: Mapped[str | None] = mapped_column(String(2048))
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    stars: Mapped[int] = mapped_column(Integer, default=0, index=True)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    language: Mapped[str | None] = mapped_column(String(100))
    topics: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    trending_rank: Mapped[int | None] = mapped_column(Integer)
    trending_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    repo_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pushed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ix_repositories_topics", topics, postgresql_using="gin"),
    )


class ArticleModel(Base):
    """News article table (raw content from AI news sites)."""

    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    external_id: Mapped[str | None] = mapped_column(String(100), index=True)
    canonical_ref: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(2048))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ix_articles_published_at_desc", published_at.desc()),
        Index("ix_articles_tags", tags, postgresql_using="gin"),
    )


class TweetModel(Base):
    """Tweet table (raw content from Twitter/X)."""

    __tablename__ = "tweets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="twitter")
    external_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    canonical_ref: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    retweets: Mapped[int] = mapped_column(Integer, default=0)
    replies: Mapped[int] = mapped_column(Integer, default=0)
    media_urls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_thread: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    __table_args__ = (
        Index("ix_tweets_published_at_desc", published_at.desc()),
    )


class TaxonomyFieldModel(Base):
    """Field taxonomy table."""

    __tablename__ = "taxonomy_fields"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("taxonomy_fields.id"))
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Self-referential relationship for hierarchy
    parent: Mapped["TaxonomyFieldModel | None"] = relationship(
        "TaxonomyFieldModel", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["TaxonomyFieldModel"]] = relationship(
        "TaxonomyFieldModel", back_populates="parent"
    )


class ProcessingRunModel(Base):
    """Processing run audit table."""

    __tablename__ = "processing_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    source: Mapped[str | None] = mapped_column(String(20), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stats: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    error: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("ix_processing_runs_started_at_desc", started_at.desc()),
    )


class FeedbackModel(Base):
    """User feedback table for evaluation."""

    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_items.id"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    actor: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Relationship
    content_item: Mapped["ContentItemModel"] = relationship(back_populates="feedbacks")


class DigestModel(Base):
    """Digest table for stored digests."""

    __tablename__ = "digests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sections: Mapped[dict[str, Any]] = mapped_column(JSONB, default=list)
    highlights: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    stats: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    version: Mapped[str] = mapped_column(String(20), default="1.0")

    __table_args__ = (
        Index("ix_digests_type_period", type, period_start, period_end),
        Index("ix_digests_generated_at_desc", generated_at.desc()),
    )


class SourceConfigModel(Base):
    """Source configuration table."""

    __tablename__ = "source_configs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    refresh_interval: Mapped[int] = mapped_column(Integer, default=60)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    last_fetched: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="active")
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
