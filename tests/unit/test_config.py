"""Tests for configuration module."""

import os
import pytest
from unittest.mock import patch

from next_epoch.config import Settings, get_settings


class TestSettings:
    """Test Settings configuration."""

    def test_default_settings(self):
        """Settings should have sensible defaults."""
        settings = Settings()
        assert settings.app_name == "Next.Epoch"
        assert settings.api_port == 8000
        assert settings.debug is False
        assert settings.environment == "development"

    def test_arxiv_default_categories(self):
        """Should track key AI arXiv categories by default."""
        settings = Settings()
        assert "cs.AI" in settings.arxiv_categories
        assert "cs.LG" in settings.arxiv_categories
        assert "cs.CL" in settings.arxiv_categories

    def test_scoring_defaults(self):
        """Scoring parameters should match spec defaults."""
        settings = Settings()
        assert settings.relevance_threshold == 0.3
        assert settings.importance_rule_weight == 0.5
        assert settings.recency_decay_hours == 168
        assert settings.novelty_enabled is False

    def test_environment_override(self):
        """Settings can be overridden via environment variables."""
        with patch.dict(os.environ, {"NEXT_EPOCH_DEBUG": "true", "NEXT_EPOCH_API_PORT": "9000"}):
            # Clear cache to get fresh settings
            get_settings.cache_clear()
            settings = Settings()
            assert settings.debug is True
            assert settings.api_port == 9000

    def test_llm_settings(self):
        """LLM settings should have defaults."""
        settings = Settings()
        assert settings.llm_provider == "openai"
        assert settings.llm_model == "gpt-4o-mini"
        assert settings.llm_temperature == 0.3

    def test_cost_controls(self):
        """Cost control settings should be present."""
        settings = Settings()
        assert settings.llm_max_cost_per_run == 1.0


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_cached(self):
        """get_settings should return cached instance."""
        get_settings.cache_clear()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
