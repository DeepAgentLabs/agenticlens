import warnings
from functools import lru_cache
from importlib import resources
from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from agenticlens.config.live_pricing import LivePricingConfig


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


def bundled_pricing_table() -> dict[str, ModelPricing]:
    """The bundled static `pricing.yaml` table, keyed by `"provider:model"`.

    Public accessor for callers that need to enumerate known models (e.g. as a
    fallback candidate pool), not just resolve a single provider/model pair.
    """
    return dict(_bundled_pricing())


def resolve_pricing(
    provider: str,
    model: str,
    overrides: dict[str, ModelPricing] | None = None,
    live_pricing: "LivePricingConfig | None" = None,
) -> ModelPricing | None:
    """Resolve pricing for a provider/model.

    Resolution order: user override -> live pricing feed (if enabled) ->
    bundled pricing.yaml -> None (unknown).
    """
    key = f"{provider}:{model}"
    if overrides and key in overrides:
        return overrides[key]

    if live_pricing is not None:
        from agenticlens.config.live_pricing import resolve_live_pricing

        pricing = resolve_live_pricing(provider, model, live_pricing)
        if pricing is not None:
            return pricing

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
    live_pricing: "LivePricingConfig | None" = None,
) -> float | None:
    pricing = resolve_pricing(provider, model, overrides, live_pricing)
    if pricing is None:
        return None
    input_cost = (prompt_tokens / 1000) * pricing.input_per_1k
    output_cost = (completion_tokens / 1000) * pricing.output_per_1k
    return input_cost + output_cost
