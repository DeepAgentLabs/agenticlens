import warnings
from functools import lru_cache
from importlib import resources

import yaml
from pydantic import BaseModel


class UnknownModelPricingWarning(UserWarning):
    """Raised when cost cannot be computed because a model has no pricing entry."""


class ModelPricing(BaseModel):
    input_per_1k: float
    output_per_1k: float


@lru_cache(maxsize=1)
def _bundled_pricing() -> dict[str, ModelPricing]:
    raw = resources.files("agenticlens.config").joinpath("pricing.yaml").read_text()
    data = yaml.safe_load(raw) or {}
    return {key: ModelPricing(**value) for key, value in data.items()}


def resolve_pricing(
    provider: str,
    model: str,
    overrides: dict[str, ModelPricing] | None = None,
) -> ModelPricing | None:
    """Resolve pricing for a provider/model.

    Resolution order: user override -> bundled pricing.yaml -> None (unknown).
    """
    key = f"{provider}:{model}"
    if overrides and key in overrides:
        return overrides[key]
    pricing = _bundled_pricing().get(key)
    if pricing is None:
        warnings.warn(
            f"No pricing entry for '{key}'. Cost will be reported as None, not $0.00.",
            UnknownModelPricingWarning,
            stacklevel=2,
        )
    return pricing


def calculate_cost(
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    overrides: dict[str, ModelPricing] | None = None,
) -> float | None:
    pricing = resolve_pricing(provider, model, overrides)
    if pricing is None:
        return None
    input_cost = (prompt_tokens / 1000) * pricing.input_per_1k
    output_cost = (completion_tokens / 1000) * pricing.output_per_1k
    return input_cost + output_cost
