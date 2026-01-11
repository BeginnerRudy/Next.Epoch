"""Relevance scoring for content items.

Implements rule-based relevance scoring as per SPEC.md:
- category_match: arXiv cs.AI/LG/CL/CV/RO, stat.ML (weight 0.4)
- keyword_density: Title/abstract keywords (weight 0.3)
- source_relevance: Source reliability (weight 0.3)
"""

import re
from dataclasses import dataclass

from next_epoch.schemas.content import ContentItem, Paper, Repository, Signal
from next_epoch.schemas.enums import ContentType, SourceType

# AI-related keywords for relevance scoring
AI_KEYWORDS = {
    "llm", "gpt", "transformer", "neural", "deep learning", "machine learning",
    "reinforcement learning", "nlp", "computer vision", "diffusion", "generative ai",
    "rag", "agent", "embedding", "fine-tuning", "inference", "benchmark", "sota",
    "state-of-the-art", "foundation model", "language model", "attention",
    "bert", "chatgpt", "claude", "gemini", "llama", "mistral", "whisper",
    "stable diffusion", "multimodal", "vision-language", "reasoning",
    "alignment", "rlhf", "prompt", "chain-of-thought", "few-shot",
}

# Relevant arXiv categories
RELEVANT_CATEGORIES = {
    "cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.RO", "cs.NE",
    "stat.ML", "cs.MA", "cs.IR", "cs.HC",
}

# Source relevance scores
SOURCE_RELEVANCE = {
    SourceType.ARXIV: 1.0,
    SourceType.GITHUB: 0.9,
    SourceType.ANTHROPIC: 1.0,
    SourceType.TWITTER: 0.7,
    SourceType.VERGE: 0.6,
    SourceType.VENTUREBEAT: 0.6,
    SourceType.TECHCRUNCH: 0.6,
    SourceType.CUSTOM: 0.5,
}


@dataclass
class RelevanceResult:
    """Result of relevance scoring."""
    score: float
    category_match: float
    keyword_density: float
    source_relevance: float
    signals: list[Signal]


def calculate_keyword_density(text: str) -> float:
    """Calculate keyword density in text.

    Returns a score between 0 and 1 based on how many AI keywords are found.
    """
    if not text:
        return 0.0

    text_lower = text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))

    # Count keyword matches
    matches = 0
    matched_keywords = []

    for keyword in AI_KEYWORDS:
        # Handle multi-word keywords
        if " " in keyword:
            if keyword in text_lower:
                matches += 1
                matched_keywords.append(keyword)
        else:
            if keyword in words:
                matches += 1
                matched_keywords.append(keyword)

    # Normalize: 0 matches = 0, 5+ matches = 1.0
    density = min(matches / 5.0, 1.0)
    return density


def calculate_category_match(categories: list[str]) -> float:
    """Calculate category match score for arXiv categories.

    Returns 1.0 if any relevant category is found, 0.5 for partial match, 0.0 otherwise.
    """
    if not categories:
        return 0.0

    category_set = set(categories)
    relevant_matches = category_set & RELEVANT_CATEGORIES

    if relevant_matches:
        # Primary AI categories get full score
        primary_ai = {"cs.AI", "cs.LG", "cs.CL", "stat.ML"}
        if relevant_matches & primary_ai:
            return 1.0
        return 0.8

    return 0.0


def score_paper_relevance(paper: Paper) -> RelevanceResult:
    """Calculate relevance score for a paper."""
    signals = []

    # Category match (weight 0.4)
    category_match = calculate_category_match(paper.categories)
    signals.append(Signal(
        key="category_match",
        value=category_match,
        weight=0.4,
        source="arxiv_categories",
    ))

    # Keyword density in title + abstract (weight 0.3)
    text = f"{paper.title} {paper.abstract}"
    keyword_density = calculate_keyword_density(text)
    signals.append(Signal(
        key="keyword_density",
        value=keyword_density,
        weight=0.3,
        source="title_abstract",
    ))

    # Source relevance (weight 0.3)
    source_relevance = SOURCE_RELEVANCE.get(SourceType.ARXIV, 0.5)
    signals.append(Signal(
        key="source_relevance",
        value=source_relevance,
        weight=0.3,
        source="source_type",
    ))

    # Calculate weighted score
    score = (
        0.4 * category_match +
        0.3 * keyword_density +
        0.3 * source_relevance
    )

    # Clamp to [0, 1]
    score = max(0.0, min(1.0, score))

    return RelevanceResult(
        score=score,
        category_match=category_match,
        keyword_density=keyword_density,
        source_relevance=source_relevance,
        signals=signals,
    )


def score_repository_relevance(repo: Repository) -> RelevanceResult:
    """Calculate relevance score for a GitHub repository."""
    signals = []

    # Topic match (similar to category match, weight 0.4)
    ai_topics = {"machine-learning", "deep-learning", "artificial-intelligence",
                 "nlp", "computer-vision", "llm", "transformers", "pytorch",
                 "tensorflow", "ai", "ml"}
    topic_set = set(t.lower() for t in (repo.topics or []))
    topic_matches = topic_set & ai_topics
    topic_match = min(len(topic_matches) / 2.0, 1.0)  # 2+ matches = 1.0

    signals.append(Signal(
        key="topic_match",
        value=topic_match,
        weight=0.4,
        source="github_topics",
    ))

    # Keyword density in name + description (weight 0.3)
    text = f"{repo.name} {repo.description or ''}"
    keyword_density = calculate_keyword_density(text)
    signals.append(Signal(
        key="keyword_density",
        value=keyword_density,
        weight=0.3,
        source="name_description",
    ))

    # Source relevance (weight 0.3)
    source_relevance = SOURCE_RELEVANCE.get(SourceType.GITHUB, 0.5)
    signals.append(Signal(
        key="source_relevance",
        value=source_relevance,
        weight=0.3,
        source="source_type",
    ))

    # Calculate weighted score
    score = (
        0.4 * topic_match +
        0.3 * keyword_density +
        0.3 * source_relevance
    )

    score = max(0.0, min(1.0, score))

    return RelevanceResult(
        score=score,
        category_match=topic_match,
        keyword_density=keyword_density,
        source_relevance=source_relevance,
        signals=signals,
    )


def score_content_relevance(content: ContentItem, raw_content: Paper | Repository | None = None) -> RelevanceResult:
    """Calculate relevance score for a ContentItem.

    If raw_content is provided, uses source-specific scoring.
    Otherwise, uses generic scoring based on ContentItem fields.
    """
    if raw_content:
        if isinstance(raw_content, Paper):
            return score_paper_relevance(raw_content)
        elif isinstance(raw_content, Repository):
            return score_repository_relevance(raw_content)

    # Generic scoring for ContentItem
    signals = []

    # Category/field match
    category_match = 0.5 if content.categories else 0.0
    signals.append(Signal(
        key="category_match",
        value=category_match,
        weight=0.4,
        source="categories",
    ))

    # Keyword density
    text = f"{content.title} {content.summary or ''}"
    keyword_density = calculate_keyword_density(text)
    signals.append(Signal(
        key="keyword_density",
        value=keyword_density,
        weight=0.3,
        source="title_summary",
    ))

    # Source relevance
    source_relevance = SOURCE_RELEVANCE.get(content.source, 0.5)
    signals.append(Signal(
        key="source_relevance",
        value=source_relevance,
        weight=0.3,
        source="source_type",
    ))

    score = (
        0.4 * category_match +
        0.3 * keyword_density +
        0.3 * source_relevance
    )

    return RelevanceResult(
        score=max(0.0, min(1.0, score)),
        category_match=category_match,
        keyword_density=keyword_density,
        source_relevance=source_relevance,
        signals=signals,
    )
