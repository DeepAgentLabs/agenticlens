import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from tokenlens.config.pricing import ModelPricing

CONFIG_ENV_VAR = "TOKENLENS_CONFIG"


class RecommenderConfig(BaseModel):
    """Thresholds used by the recommendation engine's heuristic rules."""

    system_prompt_prefix_tokens: int = 50
    max_chunks: int = 8
    history_token_limit: int = 4000


class TokenLensConfig(BaseModel):
    """Top-level configuration, loadable from pyproject.toml, YAML, or env vars."""

    pricing_overrides: dict[str, ModelPricing] = Field(default_factory=dict)
    recommender: RecommenderConfig = Field(default_factory=RecommenderConfig)


def load_config(path: str | Path | None = None) -> TokenLensConfig:
    """Load configuration from an explicit path, $TOKENLENS_CONFIG, or defaults.

    Supports a YAML file. `pyproject.toml`-based config ([tool.tokenlens]) is
    planned but not yet implemented in this scaffold.
    """
    config_path = path or os.environ.get(CONFIG_ENV_VAR)
    if config_path is None:
        return TokenLensConfig()

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"TokenLens config file not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text()) or {}
    return TokenLensConfig(**raw)
