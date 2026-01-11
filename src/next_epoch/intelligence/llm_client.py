"""LLM client using LiteLLM for multi-provider support."""

import json
from dataclasses import dataclass, field
from typing import Any

import structlog
from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential

from next_epoch.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


@dataclass
class LLMResponse:
    """Response from LLM call."""
    content: str
    model: str
    usage: dict[str, int]
    cost: float


@dataclass
class LLMUsage:
    """Track LLM usage for cost controls."""
    total_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    calls: list[dict] = field(default_factory=list)

    def add_call(self, model: str, tokens: int, cost: float) -> None:
        """Record an LLM call."""
        self.total_calls += 1
        self.total_tokens += tokens
        self.total_cost += cost
        self.calls.append({
            "model": model,
            "tokens": tokens,
            "cost": cost,
        })

    def to_dict(self) -> dict:
        """Convert to dictionary for stats."""
        return {
            "llm_calls": self.total_calls,
            "llm_tokens": self.total_tokens,
            "llm_cost_usd": round(self.total_cost, 4),
        }


class LLMClient:
    """Client for LLM calls via LiteLLM."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ):
        self.model = model or settings.llm_model
        self.api_key = api_key or (
            settings.llm_api_key.get_secret_value()
            if settings.llm_api_key else None
        )
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.temperature = temperature or settings.llm_temperature
        self.usage = LLMUsage()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Make an LLM completion call.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Override max tokens
            temperature: Override temperature
            json_mode: Request JSON response format

        Returns:
            LLMResponse with content and usage info
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature or self.temperature,
        }

        if self.api_key:
            kwargs["api_key"] = self.api_key

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        logger.debug(
            "Making LLM call",
            model=self.model,
            prompt_length=len(prompt),
        )

        response = await acompletion(**kwargs)

        # Extract response content
        content = response.choices[0].message.content

        # Calculate usage and cost
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        # Estimate cost (rough estimates, varies by model)
        cost = self._estimate_cost(
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
        )

        # Track usage
        self.usage.add_call(self.model, usage["total_tokens"], cost)

        logger.info(
            "LLM call complete",
            model=self.model,
            tokens=usage["total_tokens"],
            cost=cost,
        )

        return LLMResponse(
            content=content,
            model=self.model,
            usage=usage,
            cost=cost,
        )

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost based on model and token counts.

        These are approximate costs - actual costs vary by provider.
        """
        # Cost per 1M tokens (input, output)
        costs = {
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4o": (2.50, 10.00),
            "gpt-4-turbo": (10.00, 30.00),
            "gpt-3.5-turbo": (0.50, 1.50),
            "claude-3-haiku-20240307": (0.25, 1.25),
            "claude-3-sonnet-20240229": (3.00, 15.00),
            "claude-3-opus-20240229": (15.00, 75.00),
        }

        # Default to cheap model costs
        input_cost, output_cost = costs.get(self.model, (0.15, 0.60))

        total_cost = (
            (prompt_tokens / 1_000_000) * input_cost +
            (completion_tokens / 1_000_000) * output_cost
        )

        return total_cost

    async def complete_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> dict:
        """Make an LLM call expecting JSON response.

        Returns parsed JSON dict.
        """
        response = await self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True,
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM JSON response", content=response.content[:200])
            return {}

    def get_usage(self) -> LLMUsage:
        """Get current usage tracking."""
        return self.usage

    def reset_usage(self) -> None:
        """Reset usage tracking."""
        self.usage = LLMUsage()

    def check_cost_limit(self, limit: float | None = None) -> bool:
        """Check if cost limit has been exceeded.

        Returns True if under limit, False if exceeded.
        """
        limit = limit or settings.llm_max_cost_per_run
        return self.usage.total_cost < limit
