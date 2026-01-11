"""Intelligence layer package."""

from next_epoch.intelligence.relevance import (
    score_content_relevance,
    score_paper_relevance,
    score_repository_relevance,
    RelevanceResult,
)
from next_epoch.intelligence.importance import (
    score_content_importance,
    score_paper_importance,
    score_repository_importance,
    ImportanceResult,
)
from next_epoch.intelligence.scorer import (
    score_content,
    update_content_scores,
    ScoringResult,
)
from next_epoch.intelligence.llm_client import LLMClient, LLMResponse, LLMUsage
from next_epoch.intelligence.summarizer import Summarizer, Summary, SummaryStyle

__all__ = [
    # Relevance
    "score_content_relevance",
    "score_paper_relevance",
    "score_repository_relevance",
    "RelevanceResult",
    # Importance
    "score_content_importance",
    "score_paper_importance",
    "score_repository_importance",
    "ImportanceResult",
    # Scorer
    "score_content",
    "update_content_scores",
    "ScoringResult",
    # LLM
    "LLMClient",
    "LLMResponse",
    "LLMUsage",
    # Summarizer
    "Summarizer",
    "Summary",
    "SummaryStyle",
]
