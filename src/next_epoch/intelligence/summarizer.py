"""Content summarizer using LLM."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import structlog

from next_epoch.intelligence.llm_client import LLMClient
from next_epoch.schemas.content import Paper, Repository, ContentItem

logger = structlog.get_logger()


class SummaryStyle(str, Enum):
    """Summary style options."""
    BRIEF = "brief"
    DETAILED = "detailed"
    ELI5 = "eli5"
    TECHNICAL = "technical"


@dataclass
class Summary:
    """Generated summary."""
    content_id: str
    style: SummaryStyle
    summary: str
    key_points: list[str]
    generated_at: datetime
    model: str
    cost: float


# System prompts for different styles
SYSTEM_PROMPTS = {
    SummaryStyle.BRIEF: """You are an AI research summarizer. Create concise, informative summaries.
Focus on: main contribution, key results, practical implications.
Keep summaries under 100 words.""",

    SummaryStyle.DETAILED: """You are an AI research summarizer. Create comprehensive summaries.
Include: problem statement, methodology, key findings, limitations, implications.
Target length: 200-300 words.""",

    SummaryStyle.ELI5: """You are an AI explainer. Explain complex research in simple terms.
Use analogies and everyday language. Avoid jargon.
Target audience: intelligent non-experts.""",

    SummaryStyle.TECHNICAL: """You are a technical AI researcher. Create precise technical summaries.
Include: architecture details, training approach, evaluation metrics, comparisons.
Use technical terminology appropriately.""",
}


def build_paper_prompt(paper: Paper, style: SummaryStyle) -> str:
    """Build summarization prompt for a paper."""
    prompt = f"""Summarize this AI research paper:

Title: {paper.title}

Authors: {', '.join(a.name for a in paper.authors[:5])}

Categories: {', '.join(paper.categories)}

Abstract:
{paper.abstract}

Provide:
1. A {style.value} summary
2. 3-5 key points as bullet points

Format your response as JSON:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...]
}}"""
    return prompt


def build_repository_prompt(repo: Repository, style: SummaryStyle) -> str:
    """Build summarization prompt for a repository."""
    topics = ", ".join(repo.topics) if repo.topics else "N/A"

    prompt = f"""Summarize this GitHub repository:

Name: {repo.full_name}
Description: {repo.description or 'No description'}
Language: {repo.language or 'Unknown'}
Topics: {topics}
Stars: {repo.stars:,}

Provide:
1. A {style.value} summary of what this project does
2. 3-5 key features or highlights

Format your response as JSON:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...]
}}"""
    return prompt


class Summarizer:
    """Content summarizer using LLM."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    async def summarize_paper(
        self,
        paper: Paper,
        style: SummaryStyle = SummaryStyle.BRIEF,
    ) -> Summary:
        """Generate a summary for a research paper."""
        prompt = build_paper_prompt(paper, style)
        system_prompt = SYSTEM_PROMPTS[style]

        logger.info(
            "Summarizing paper",
            paper_id=paper.external_id,
            style=style.value,
        )

        response = await self.llm.complete_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        summary_text = response.get("summary", "Summary not available.")
        key_points = response.get("key_points", [])

        return Summary(
            content_id=paper.id,
            style=style,
            summary=summary_text,
            key_points=key_points,
            generated_at=datetime.utcnow(),
            model=self.llm.model,
            cost=self.llm.usage.total_cost,
        )

    async def summarize_repository(
        self,
        repo: Repository,
        style: SummaryStyle = SummaryStyle.BRIEF,
    ) -> Summary:
        """Generate a summary for a GitHub repository."""
        prompt = build_repository_prompt(repo, style)
        system_prompt = SYSTEM_PROMPTS[style]

        logger.info(
            "Summarizing repository",
            repo=repo.full_name,
            style=style.value,
        )

        response = await self.llm.complete_json(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        summary_text = response.get("summary", "Summary not available.")
        key_points = response.get("key_points", [])

        return Summary(
            content_id=repo.id,
            style=style,
            summary=summary_text,
            key_points=key_points,
            generated_at=datetime.utcnow(),
            model=self.llm.model,
            cost=self.llm.usage.total_cost,
        )

    async def summarize_content(
        self,
        content: ContentItem,
        raw_content: Paper | Repository | None = None,
        style: SummaryStyle = SummaryStyle.BRIEF,
    ) -> Summary:
        """Generate a summary for any content type."""
        if raw_content:
            if isinstance(raw_content, Paper):
                return await self.summarize_paper(raw_content, style)
            elif isinstance(raw_content, Repository):
                return await self.summarize_repository(raw_content, style)

        # Fallback: summarize from ContentItem fields
        prompt = f"""Summarize this content:

Title: {content.title}
Type: {content.type.value}
Source: {content.source.value}

{content.summary or 'No additional details available.'}

Provide a {style.value} summary and 3-5 key points.

Format as JSON:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...]
}}"""

        response = await self.llm.complete_json(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPTS[style],
        )

        return Summary(
            content_id=content.id,
            style=style,
            summary=response.get("summary", "Summary not available."),
            key_points=response.get("key_points", []),
            generated_at=datetime.utcnow(),
            model=self.llm.model,
            cost=self.llm.usage.total_cost,
        )

    def get_usage(self):
        """Get LLM usage statistics."""
        return self.llm.get_usage()
