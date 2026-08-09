import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agenticlens.config.live_pricing import (
    LivePricingConfig,
    get_live_pricing_table,
    resolve_live_pricing,
)
from agenticlens.config.pricing import calculate_cost, resolve_pricing

_FAKE_TABLE = {
    "gpt-4o": {"input_cost_per_token": 0.000011, "output_cost_per_token": 0.000022},
    "claude-3-5-sonnet-20241022": {
        "input_cost_per_token": 0.000003,
        "output_cost_per_token": 0.000015,
    },
}


def _mock_urlopen(data: dict) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = json.dumps(data).encode()
    return response


@pytest.fixture
def live_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> LivePricingConfig:
    monkeypatch.delenv("AGENTICLENS_DISABLE_LIVE_PRICING", raising=False)
    return LivePricingConfig(cache_path=str(tmp_path / "cache.json"))


def test_resolve_live_pricing_fetches_and_converts_per_token_to_per_1k(
    live_config: LivePricingConfig,
) -> None:
    with patch("json.load", return_value=_FAKE_TABLE), patch("urllib.request.urlopen"):
        pricing = resolve_live_pricing("openai", "gpt-4o", live_config)

    assert pricing is not None
    assert pricing.input_per_1k == pytest.approx(0.011)
    assert pricing.output_per_1k == pytest.approx(0.022)


def test_resolve_live_pricing_uses_alias_for_versioned_model_names(
    live_config: LivePricingConfig,
) -> None:
    with patch("json.load", return_value=_FAKE_TABLE), patch("urllib.request.urlopen"):
        pricing = resolve_live_pricing("anthropic", "claude-3-5-sonnet", live_config)

    assert pricing is not None
    assert pricing.input_per_1k == pytest.approx(0.003)


def test_live_pricing_cache_avoids_refetch_within_ttl(live_config: LivePricingConfig) -> None:
    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch("json.load", return_value=_FAKE_TABLE),
    ):
        get_live_pricing_table(live_config)
        get_live_pricing_table(live_config)

    assert mock_urlopen.call_count == 1


def test_live_pricing_falls_back_to_stale_cache_on_fetch_failure(
    live_config: LivePricingConfig,
) -> None:
    with (
        patch("urllib.request.urlopen"),
        patch("json.load", return_value=_FAKE_TABLE),
    ):
        get_live_pricing_table(live_config)

    stale_config = live_config.model_copy(update={"ttl_seconds": 0.0001})
    with patch("urllib.request.urlopen", side_effect=OSError("network down")):
        table = get_live_pricing_table(stale_config)

    assert table == _FAKE_TABLE


def test_live_pricing_returns_none_when_unreachable_and_no_cache(
    live_config: LivePricingConfig,
) -> None:
    with patch("urllib.request.urlopen", side_effect=OSError("network down")):
        table = get_live_pricing_table(live_config)

    assert table is None


def test_resolve_pricing_falls_back_to_static_when_live_disabled(
    live_config: LivePricingConfig,
) -> None:
    live_config.enabled = False
    with patch("urllib.request.urlopen") as mock_urlopen:
        pricing = resolve_pricing("openai", "gpt-4o-mini", live_pricing=live_config)

    mock_urlopen.assert_not_called()
    assert pricing is not None
    assert pricing.input_per_1k == pytest.approx(0.00015)


def test_resolve_pricing_prefers_live_over_static(live_config: LivePricingConfig) -> None:
    with patch("json.load", return_value=_FAKE_TABLE), patch("urllib.request.urlopen"):
        pricing = resolve_pricing("openai", "gpt-4o", live_pricing=live_config)

    assert pricing is not None
    assert pricing.input_per_1k == pytest.approx(0.011)


def test_calculate_cost_uses_live_pricing_when_provided(live_config: LivePricingConfig) -> None:
    with patch("json.load", return_value=_FAKE_TABLE), patch("urllib.request.urlopen"):
        cost = calculate_cost(
            "openai", "gpt-4o", prompt_tokens=1000, completion_tokens=1000, live_pricing=live_config
        )

    assert cost == pytest.approx(0.011 + 0.022)


def test_env_var_disables_live_pricing_even_when_config_enabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AGENTICLENS_DISABLE_LIVE_PRICING", "1")
    config = LivePricingConfig(cache_path=str(tmp_path / "cache.json"))

    with patch("urllib.request.urlopen") as mock_urlopen:
        table = get_live_pricing_table(config)

    mock_urlopen.assert_not_called()
    assert table is None
