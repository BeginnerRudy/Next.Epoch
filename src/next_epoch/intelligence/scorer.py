"""Combined scorer for content items.

Combines relevance, importance, and calculates frontier score.
"""

from dataclasses import dataclass
from datetime import datetime

from next_epoch.config import get_settings
from next_epoch.schemas.content import ContentItem, Paper, Repository, ScoreBreakdown, Signal
from next_epoch.intelligence.relevance import score_content_relevance, RelevanceResult
from next_epoch.intelligence.importance import score_content_importance, ImportanceResult

settings = get_settings()


@dataclass
class ScoringResult:
    """Complete scoring result for a content item."""
    relevance_score: float
    importance_score: float
    novelty_score: float | None
    frontier_score: float | None
    score_breakdown: ScoreBreakdown
    signals: list[Signal]
    is_relevant: bool  # Passes relevance threshold


def calculate_recency_boost(published_at: datetime) -> float:
    """Calculate recency boost that decays over time.

    Formula: max(0, 1 - hours_since_published / decay_hours)
    """
    now = datetime.utcnow()
    hours_since = (now - published_at).total_seconds() / 3600
    decay_hours = settings.recency_decay_hours  # Default 168 (7 days)

    boost = max(0.0, 1.0 - hours_since / decay_hours)
    return boost


def calculate_frontier_score(
    relevance: float,
    importance: float,
    novelty: float | None,
    recency_boost: float,
) -> float:
    """Calculate frontier score using weighted combination.

    Formula (from SPEC.md):
    frontier = 0.2 * relevance + 0.5 * importance + 0.2 * novelty + 0.1 * recency

    If novelty is not available, redistribute weight to importance.
    """
    if novelty is not None:
        frontier = (
            0.2 * relevance +
            0.5 * importance +
            0.2 * novelty +
            0.1 * recency_boost
        )
    else:
        # No novelty score - redistribute weight
        frontier = (
            0.25 * relevance +
            0.65 * importance +
            0.1 * recency_boost
        )

    return max(0.0, min(1.0, frontier))


def score_content(
    content: ContentItem,
    raw_content: Paper | Repository | None = None,
) -> ScoringResult:
    """Score a content item comprehensively.

    Args:
        content: The ContentItem to score
        raw_content: Optional raw content (Paper, Repository) for detailed scoring

    Returns:
        ScoringResult with all scores and signals
    """
    # Calculate relevance
    relevance_result = score_content_relevance(content, raw_content)

    # Check relevance threshold
    is_relevant = relevance_result.score >= settings.relevance_threshold

    # Calculate importance
    importance_result = score_content_importance(content, raw_content)

    # Novelty is deferred for MVP (requires comparing to recent items)
    novelty_score = None
    if settings.novelty_enabled:
        # Would implement novelty scoring here
        novelty_score = None

    # Calculate recency boost
    recency_boost = calculate_recency_boost(content.published_at)

    # Calculate frontier score
    frontier_score = calculate_frontier_score(
        relevance_result.score,
        importance_result.score,
        novelty_score,
        recency_boost,
    )

    # Combine signals
    all_signals = relevance_result.signals + importance_result.signals
    all_signals.append(Signal(
        key="recency_boost",
        value=recency_boost,
        weight=0.1,
        source="published_at",
    ))

    # Build explanation
    explanations = []
    if relevance_result.score >= 0.7:
        explanations.append("highly relevant")
    elif relevance_result.score >= 0.5:
        explanations.append("relevant")

    if importance_result.explanation != "Standard content":
        explanations.append(importance_result.explanation.replace("High importance: ", ""))

    if recency_boost >= 0.8:
        explanations.append("very recent")
    elif recency_boost >= 0.5:
        explanations.append("recent")

    explanation = "; ".join(explanations) if explanations else None

    # Build score breakdown
    breakdown = ScoreBreakdown(
        relevance=relevance_result.score,
        importance=importance_result.score,
        novelty=novelty_score,
        frontier=frontier_score,
        explanation=explanation,
    )

    return ScoringResult(
        relevance_score=relevance_result.score,
        importance_score=importance_result.score,
        novelty_score=novelty_score,
        frontier_score=frontier_score,
        score_breakdown=breakdown,
        signals=all_signals,
        is_relevant=is_relevant,
    )


def update_content_scores(
    content: ContentItem,
    raw_content: Paper | Repository | None = None,
) -> ContentItem:
    """Score content and update the ContentItem with scores.

    Returns a new ContentItem with updated scores.
    """
    result = score_content(content, raw_content)

    # Create updated content item
    return ContentItem(
        id=content.id,
        type=content.type,
        source=content.source,
        title=content.title,
        summary=content.summary,
        url=content.url,
        relevance_score=result.relevance_score,
        importance_score=result.importance_score,
        novelty_score=result.novelty_score,
        frontier_score=result.frontier_score,
        score_breakdown=result.score_breakdown,
        tags=content.tags,
        categories=content.categories,
        published_at=content.published_at,
        processed_at=content.processed_at,
        fields=content.fields,
        signals=result.signals,
        provenance=content.provenance,
        raw_content_type=content.raw_content_type,
        raw_content_id=content.raw_content_id,
    )
