import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from agenticlens.config.live_pricing import LivePricingConfig
from agenticlens.config.pricing import ModelPricing

CONFIG_ENV_VAR = "AGENTICLENS_CONFIG"

# Direct, first-party model providers considered for model-swap comparisons.
# Deliberately excludes gateway/reseller `litellm_provider` values (bedrock,
# azure, vertex_ai-*, openrouter, replicate, ...) that just re-host the same
# underlying models -- comparing against those isn't a genuine model swap,
# it's an infrastructure decision, and would drown out real cross-provider
# findings. Widen this list if you want those comparisons too.
DEFAULT_MODEL_SWAP_PROVIDERS: list[str] = [
    "openai",
    "anthropic",
    "gemini",
    "mistral",
    "xai",
    "deepseek",
    "groq",
    "cohere_chat",
    "perplexity",
]


class RecommenderConfig(BaseModel):
    """Thresholds used by the recommendation engine's heuristic rules."""

    system_prompt_prefix_tokens: int = 50
    max_chunks: int = 8
    history_token_limit: int = 4000
    monthly_runs: int = 1000
    warning_savings_pct: float = 5.0
    critical_savings_pct: float = 20.0
    warning_savings_usd: float = 0.005
    critical_savings_usd: float = 0.05
    rag_min_chunk_utility_score: float = 0.08
    rag_min_low_utility_chunks: int = 2
    handoff_token_limit: int = 3000
    model_swap_min_savings_pct: float = 15.0
    model_swap_providers: list[str] = Field(
        default_factory=lambda: list(DEFAULT_MODEL_SWAP_PROVIDERS)
    )


class AgenticLensConfig(BaseModel):
    """Top-level configuration, loadable from pyproject.toml, YAML, or env vars."""

    pricing_overrides: dict[str, ModelPricing] = Field(default_factory=dict)
    live_pricing: LivePricingConfig = Field(default_factory=LivePricingConfig)
    recommender: RecommenderConfig = Field(default_factory=RecommenderConfig)


def load_config(path: str | Path | None = None) -> AgenticLensConfig:
    """Load configuration from an explicit path, $AGENTICLENS_CONFIG, or defaults.

    Supports a YAML file. `pyproject.toml`-based config ([tool.agenticlens]) is
    planned but not yet implemented in this scaffold.
    """
    config_path = path or os.environ.get(CONFIG_ENV_VAR)
    if config_path is None:
        return AgenticLensConfig()

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"AgenticLens config file not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text()) or {}
    return AgenticLensConfig(**raw)
