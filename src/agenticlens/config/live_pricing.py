"""Live pricing resolution backed by LiteLLM's community-maintained pricing feed.

Resolution order lives in `pricing.resolve_pricing`; this module only knows how
to fetch/cache the remote table and look a `provider:model` pair up in it.
"""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from agenticlens.config.pricing import ModelPricing

LITELLM_PRICING_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
)
DEFAULT_CACHE_PATH = Path.home() / ".cache" / "agenticlens" / "live_pricing_cache.json"
DEFAULT_TTL_SECONDS = 24 * 60 * 60
DEFAULT_TIMEOUT_SECONDS = 5.0

# Kill switch for hermetic/offline environments (e.g. this project's own test suite).
DISABLE_ENV_VAR = "AGENTICLENS_DISABLE_LIVE_PRICING"

# Our bundled provider:model keys don't always match LiteLLM's flat model-name
# keys (which are versioned, e.g. "claude-3-5-sonnet-20241022"). Extend this as
# more aliases are needed.
_LITELLM_KEY_ALIASES: dict[str, str] = {
    "anthropic:claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
    "anthropic:claude-3-5-haiku": "claude-3-5-haiku-20241022",
}


class LivePricingConfig(BaseModel):
    """Settings controlling live pricing lookups against LiteLLM's feed."""

    enabled: bool = True
    url: str = LITELLM_PRICING_URL
    cache_path: str = str(DEFAULT_CACHE_PATH)
    ttl_seconds: float = Field(default=DEFAULT_TTL_SECONDS, gt=0)
    timeout_seconds: float = Field(default=DEFAULT_TIMEOUT_SECONDS, gt=0)


def _litellm_lookup_keys(provider: str, model: str) -> list[str]:
    key = f"{provider}:{model}"
    candidates = [_LITELLM_KEY_ALIASES.get(key, model), model, f"{provider}/{model}"]
    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)
    return ordered


def parse_litellm_entry(entry: dict[str, Any]) -> ModelPricing | None:
    input_per_token = entry.get("input_cost_per_token")
    output_per_token = entry.get("output_cost_per_token")
    if input_per_token is None or output_per_token is None:
        return None
    return ModelPricing(
        input_per_1k=float(input_per_token) * 1000,
        output_per_1k=float(output_per_token) * 1000,
    )


def _fetch_remote(url: str, timeout_seconds: float) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout_seconds) as resp:  # noqa: S310
        return json.load(resp)  # type: ignore[no-any-return]


def _read_cache(cache_path: Path) -> tuple[float, dict[str, Any]] | None:
    if not cache_path.exists():
        return None
    try:
        payload = json.loads(cache_path.read_text())
        return payload["fetched_at"], payload["data"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def _write_cache(cache_path: Path, data: dict[str, Any]) -> None:
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps({"fetched_at": time.time(), "data": data}))
    except OSError:
        pass  # Cache is a performance optimization, not a correctness requirement.


def get_live_pricing_table(config: LivePricingConfig) -> dict[str, Any] | None:
    """Return the raw LiteLLM pricing table, refreshing the on-disk cache if stale.

    Returns None when no fresh fetch succeeds and no prior cache exists -- callers
    should fall back to bundled static pricing in that case.
    """
    if os.environ.get(DISABLE_ENV_VAR):
        return None

    cache_path = Path(config.cache_path)
    cached = _read_cache(cache_path)
    if cached is not None and (time.time() - cached[0]) < config.ttl_seconds:
        return cached[1]

    try:
        data = _fetch_remote(config.url, config.timeout_seconds)
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError, ValueError):
        return cached[1] if cached is not None else None

    _write_cache(cache_path, data)
    return data


def resolve_live_pricing(
    provider: str, model: str, config: LivePricingConfig
) -> ModelPricing | None:
    """Look up `provider:model` pricing from the live LiteLLM feed (cached, TTL'd)."""
    if not config.enabled:
        return None

    table = get_live_pricing_table(config)
    if table is None:
        return None

    for key in _litellm_lookup_keys(provider, model):
        entry = table.get(key)
        if entry:
            pricing = parse_litellm_entry(entry)
            if pricing is not None:
                return pricing
    return None
