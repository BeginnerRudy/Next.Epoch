"""Configuration management for Next.Epoch."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="NEXT_EPOCH_",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Next.Epoch"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    api_key: SecretStr | None = Field(None, description="Default API key for authentication")

    # Database
    database_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/next_epoch",
        description="PostgreSQL connection URL (async)",
    )
    database_url_sync: str = Field(
        "postgresql://postgres:postgres@localhost:5432/next_epoch",
        description="PostgreSQL connection URL (sync, for migrations)",
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM Configuration
    llm_provider: str = "openai"  # or "anthropic", "together", etc.
    llm_model: str = "gpt-4o-mini"
    llm_api_key: SecretStr | None = None
    llm_max_tokens: int = 1000
    llm_temperature: float = 0.3

    # Cost Controls
    llm_max_cost_per_run: float = Field(
        1.0, description="Maximum LLM cost per processing run in USD"
    )

    # Ingestion Settings
    arxiv_categories: list[str] = Field(
        default=["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.RO", "stat.ML"],
        description="arXiv categories to track",
    )
    arxiv_max_results: int = 100
    github_trending_languages: list[str] = Field(
        default=["python", "jupyter-notebook", ""],  # "" = all languages
        description="Languages to track on GitHub Trending",
    )

    # Scheduling
    ingestion_interval_minutes: int = 60
    scoring_interval_minutes: int = 120

    # Scoring Thresholds
    relevance_threshold: float = 0.3
    importance_rule_weight: float = 0.5
    novelty_enabled: bool = False
    recency_decay_hours: int = 168  # 7 days

    # Network / Proxy
    http_proxy: str | None = Field(
        None, description="HTTP proxy URL for external requests (e.g., arXiv in China)"
    )

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "console"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
