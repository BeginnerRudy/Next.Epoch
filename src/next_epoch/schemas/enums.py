"""Enumeration types for Next.Epoch."""

from enum import Enum


class SourceType(str, Enum):
    """Content source types."""

    ARXIV = "arxiv"
    GITHUB = "github"
    TWITTER = "twitter"
    ANTHROPIC = "anthropic"
    VERGE = "verge"
    VENTUREBEAT = "venturebeat"
    TECHCRUNCH = "techcrunch"
    CUSTOM = "custom"


class ContentType(str, Enum):
    """Content item types."""

    PAPER = "paper"
    ARTICLE = "article"
    REPOSITORY = "repository"
    SOCIAL = "social"
    ANNOUNCEMENT = "announcement"
    APPLICATION = "application"  # AI-powered products and tools
    CASE_STUDY = "case_study"  # Real-world deployment stories


class DigestType(str, Enum):
    """Digest types."""

    FLASH = "flash"
    DAILY = "daily"
    WEEKLY = "weekly"
    DEEP_DIVE = "deep_dive"


class AnnouncementType(str, Enum):
    """Announcement types."""

    PRODUCT_LAUNCH = "product_launch"
    RESEARCH_RELEASE = "research_release"
    BLOG_POST = "blog_post"
    PRESS_RELEASE = "press_release"
    OTHER = "other"


class TrendMomentum(str, Enum):
    """Trend momentum direction."""

    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


class FieldStatus(str, Enum):
    """Field taxonomy status."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"


class RunType(str, Enum):
    """Processing run types."""

    INGEST = "ingest"
    ENRICH = "enrich"
    SUMMARIZE = "summarize"
    SCORE = "score"
    DIGEST = "digest"


class RunStatus(str, Enum):
    """Processing run status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class FeedbackKind(str, Enum):
    """Feedback kinds for evaluation."""

    RELEVANCE = "relevance"
    VALUE = "value"
    SUMMARY_QUALITY = "summary_quality"
