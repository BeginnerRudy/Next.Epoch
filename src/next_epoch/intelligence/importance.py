"""Importance scoring for content items.

Implements hybrid importance scoring as per SPEC.md:
- 50% rule-based signals
- 50% LLM judgment (when available)

Rule-based signals:
- author_authority: From known labs (0.15)
- has_code: Code repository linked (0.10)
- has_dataset: Dataset mentioned (0.05)
- stars_velocity: GitHub stars in 24h (0.10)
- cross_mentions: Referenced elsewhere (0.10)
"""

import re
from dataclasses import dataclass

from next_epoch.schemas.content import Article, ContentItem, Paper, Repository, Signal

# Known AI labs and institutions for authority scoring
KNOWN_LABS = {
    "openai", "anthropic", "deepmind", "google", "meta", "microsoft",
    "nvidia", "stanford", "mit", "berkeley", "cmu", "carnegie mellon",
    "harvard", "princeton", "oxford", "cambridge", "tsinghua", "peking",
    "allen institute", "ai2", "fair", "brain", "research",
}

# Known AI companies for article importance
AI_COMPANIES = {
    "openai", "anthropic", "google", "deepmind", "meta", "microsoft",
    "nvidia", "amazon", "aws", "ibm", "salesforce", "adobe", "oracle",
    "hugging face", "stability ai", "midjourney", "cohere", "replicate",
    "notion", "stripe", "shopify", "slack", "zoom", "github",
}

# Patterns for detecting code/dataset mentions
CODE_PATTERNS = [
    r"github\.com/\w+/\w+",
    r"code is available",
    r"code available at",
    r"our code",
    r"implementation available",
    r"open.?source",
]

DATASET_PATTERNS = [
    r"dataset",
    r"benchmark",
    r"we release",
    r"publicly available data",
    r"training data",
]


@dataclass
class ImportanceResult:
    """Result of importance scoring."""
    score: float
    rule_score: float
    llm_score: float | None
    signals: list[Signal]
    explanation: str


def check_author_authority(authors: list[dict] | None) -> tuple[float, list[str]]:
    """Check if authors are from known labs/institutions.

    Returns (score, matched_affiliations).
    """
    if not authors:
        return 0.0, []

    matched = []
    for author in authors:
        name = (author.get("name") or "").lower()
        affiliation = (author.get("affiliation") or "").lower()

        for lab in KNOWN_LABS:
            if lab in affiliation or lab in name:
                matched.append(lab)
                break

    # Score based on percentage of authors from known labs
    if not authors:
        return 0.0, matched

    score = min(len(matched) / len(authors), 1.0)
    return score, list(set(matched))


def check_has_code(text: str) -> bool:
    """Check if text mentions code availability."""
    text_lower = text.lower()
    for pattern in CODE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def check_has_dataset(text: str) -> bool:
    """Check if text mentions dataset release."""
    text_lower = text.lower()
    for pattern in DATASET_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def calculate_stars_velocity_score(stars: int, trending_rank: int | None = None) -> float:
    """Calculate score based on GitHub stars and trending rank.

    Higher stars and better trending rank = higher score.
    """
    # Base score from stars
    if stars >= 10000:
        star_score = 1.0
    elif stars >= 5000:
        star_score = 0.9
    elif stars >= 1000:
        star_score = 0.7
    elif stars >= 500:
        star_score = 0.5
    elif stars >= 100:
        star_score = 0.3
    else:
        star_score = 0.1

    # Boost from trending rank
    if trending_rank:
        if trending_rank <= 5:
            star_score = min(star_score + 0.3, 1.0)
        elif trending_rank <= 10:
            star_score = min(star_score + 0.2, 1.0)
        elif trending_rank <= 25:
            star_score = min(star_score + 0.1, 1.0)

    return star_score


def score_paper_importance(paper: Paper) -> ImportanceResult:
    """Calculate importance score for a paper using rule-based signals."""
    signals = []
    explanations = []

    # Author authority (weight 0.15 of rule score, so 0.30 effective)
    authors_data = [{"name": a.name, "affiliation": a.affiliation} for a in paper.authors]
    authority_score, matched_labs = check_author_authority(authors_data)
    signals.append(Signal(
        key="author_authority",
        value=authority_score,
        weight=0.30,
        source="author_affiliations",
    ))
    if matched_labs:
        explanations.append(f"from {', '.join(matched_labs[:3])}")

    # Has code (weight 0.10 of rule score, so 0.20 effective)
    text = f"{paper.title} {paper.abstract}"
    has_code = check_has_code(text)
    code_score = 1.0 if has_code else 0.0
    signals.append(Signal(
        key="has_code",
        value=has_code,
        weight=0.20,
        source="abstract",
    ))
    if has_code:
        explanations.append("includes code")

    # Has dataset (weight 0.05 of rule score, so 0.10 effective)
    has_dataset = check_has_dataset(text)
    dataset_score = 1.0 if has_dataset else 0.0
    signals.append(Signal(
        key="has_dataset",
        value=has_dataset,
        weight=0.10,
        source="abstract",
    ))
    if has_dataset:
        explanations.append("releases dataset/benchmark")

    # Cross mentions - placeholder (would require cross-referencing)
    cross_mentions = 0.0
    signals.append(Signal(
        key="cross_mentions",
        value=cross_mentions,
        weight=0.20,
        source="cross_reference",
    ))

    # Content quality indicators (additional weight)
    # Check for benchmark results, SOTA claims, etc.
    sota_patterns = ["state-of-the-art", "sota", "outperform", "surpass", "new benchmark"]
    has_sota = any(p in text.lower() for p in sota_patterns)
    sota_score = 1.0 if has_sota else 0.0
    signals.append(Signal(
        key="claims_sota",
        value=has_sota,
        weight=0.20,
        source="abstract",
    ))
    if has_sota:
        explanations.append("claims SOTA results")

    # Calculate rule-based score
    rule_score = (
        0.30 * authority_score +
        0.20 * code_score +
        0.10 * dataset_score +
        0.20 * cross_mentions +
        0.20 * sota_score
    )

    # No LLM score for now (would be added async)
    llm_score = None

    # Final score (100% rules for now, would be 50/50 with LLM)
    final_score = rule_score

    explanation = "High importance: " + ", ".join(explanations) if explanations else "Standard content"

    return ImportanceResult(
        score=max(0.0, min(1.0, final_score)),
        rule_score=rule_score,
        llm_score=llm_score,
        signals=signals,
        explanation=explanation,
    )


def score_repository_importance(repo: Repository) -> ImportanceResult:
    """Calculate importance score for a GitHub repository."""
    signals = []
    explanations = []

    # Stars velocity (weight 0.40)
    stars_score = calculate_stars_velocity_score(repo.stars, repo.trending_rank)
    signals.append(Signal(
        key="stars_velocity",
        value=repo.stars,
        weight=0.40,
        source="github_stars",
    ))
    if repo.stars >= 1000:
        explanations.append(f"{repo.stars:,} stars")

    # Trending rank (weight 0.30)
    trending_score = 0.0
    if repo.trending_rank:
        if repo.trending_rank <= 5:
            trending_score = 1.0
        elif repo.trending_rank <= 10:
            trending_score = 0.8
        elif repo.trending_rank <= 25:
            trending_score = 0.5
        else:
            trending_score = 0.3
        signals.append(Signal(
            key="trending_rank",
            value=repo.trending_rank,
            weight=0.30,
            source="github_trending",
        ))
        if repo.trending_rank <= 10:
            explanations.append(f"trending #{repo.trending_rank}")

    # Has documentation/README quality - proxy via description length
    desc_length = len(repo.description or "")
    doc_score = min(desc_length / 200, 1.0)  # 200+ chars = full score
    signals.append(Signal(
        key="documentation_quality",
        value=doc_score,
        weight=0.15,
        source="description",
    ))

    # Active development - proxy via recent push
    # (would need actual push date comparison)
    active_score = 0.5  # Default assumption
    signals.append(Signal(
        key="active_development",
        value=active_score,
        weight=0.15,
        source="push_date",
    ))

    # Calculate rule-based score
    rule_score = (
        0.40 * stars_score +
        0.30 * trending_score +
        0.15 * doc_score +
        0.15 * active_score
    )

    llm_score = None
    final_score = rule_score

    explanation = "High importance: " + ", ".join(explanations) if explanations else "Standard repository"

    return ImportanceResult(
        score=max(0.0, min(1.0, final_score)),
        rule_score=rule_score,
        llm_score=llm_score,
        signals=signals,
        explanation=explanation,
    )


def score_article_importance(article: Article) -> ImportanceResult:
    """Calculate importance score for a news article.

    Importance signals for articles:
    - company_mention: Major AI company mentioned (0.35)
    - impact_indicators: Metrics like users, revenue, adoption (0.25)
    - recency: Recent news is more important (0.20)
    - content_depth: Length and detail of article (0.20)
    """
    signals = []
    explanations = []
    text = f"{article.title} {article.excerpt} {article.content}".lower()

    # Company mention score (weight 0.35)
    mentioned_companies = []
    for company in AI_COMPANIES:
        if company in text:
            mentioned_companies.append(company)

    company_score = min(len(mentioned_companies) / 2.0, 1.0)  # 2+ companies = full score
    signals.append(Signal(
        key="company_mention",
        value=company_score,
        weight=0.35,
        source="article_content",
    ))
    if mentioned_companies:
        explanations.append(f"mentions {', '.join(mentioned_companies[:2])}")

    # Impact indicators (weight 0.25)
    impact_patterns = [
        r"\d+\s*million\s*(users|customers)",
        r"\d+\s*billion",
        r"\d+%\s*(increase|growth|improvement)",
        r"\$\d+",
        r"enterprise",
        r"production",
        r"scale",
    ]
    impact_count = sum(1 for p in impact_patterns if re.search(p, text))
    impact_score = min(impact_count / 3.0, 1.0)  # 3+ impact mentions = full score
    signals.append(Signal(
        key="impact_indicators",
        value=impact_score,
        weight=0.25,
        source="article_content",
    ))
    if impact_count >= 2:
        explanations.append("significant impact metrics")

    # Recency score (weight 0.20) - news is time-sensitive
    # For now, give full recency score (actual implementation would check date)
    recency_score = 0.8  # Assume recent since we just collected it
    signals.append(Signal(
        key="recency",
        value=recency_score,
        weight=0.20,
        source="published_date",
    ))

    # Content depth (weight 0.20) - proxy via content length
    content_length = len(article.content or "")
    depth_score = min(content_length / 500, 1.0)  # 500+ chars = full score
    signals.append(Signal(
        key="content_depth",
        value=depth_score,
        weight=0.20,
        source="content_length",
    ))

    # Calculate rule-based score
    rule_score = (
        0.35 * company_score +
        0.25 * impact_score +
        0.20 * recency_score +
        0.20 * depth_score
    )

    llm_score = None
    final_score = rule_score

    explanation = "High importance: " + ", ".join(explanations) if explanations else "Standard news article"

    return ImportanceResult(
        score=max(0.0, min(1.0, final_score)),
        rule_score=rule_score,
        llm_score=llm_score,
        signals=signals,
        explanation=explanation,
    )


def score_content_importance(
    content: ContentItem,
    raw_content: Paper | Repository | Article | None = None
) -> ImportanceResult:
    """Calculate importance score for a ContentItem."""
    if raw_content:
        if isinstance(raw_content, Paper):
            return score_paper_importance(raw_content)
        elif isinstance(raw_content, Repository):
            return score_repository_importance(raw_content)
        elif isinstance(raw_content, Article):
            return score_article_importance(raw_content)

    # Generic scoring
    signals = []
    rule_score = 0.5  # Default moderate importance

    signals.append(Signal(
        key="generic_importance",
        value=rule_score,
        weight=1.0,
        source="default",
    ))

    return ImportanceResult(
        score=rule_score,
        rule_score=rule_score,
        llm_score=None,
        signals=signals,
        explanation="Standard content",
    )
