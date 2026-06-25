import pytest

from tokenlens.config.pricing import ModelPricing, UnknownModelPricingWarning, calculate_cost


def test_calculate_cost_known_model() -> None:
    cost = calculate_cost("openai", "gpt-4o-mini", prompt_tokens=1000, completion_tokens=1000)
    assert cost == pytest.approx(0.00015 + 0.0006)


def test_calculate_cost_unknown_model_returns_none_and_warns() -> None:
    with pytest.warns(UnknownModelPricingWarning):
        cost = calculate_cost(
            "openai", "not-a-real-model", prompt_tokens=100, completion_tokens=100
        )
    assert cost is None


def test_calculate_cost_override_wins() -> None:
    overrides = {"openai:gpt-4o-mini": ModelPricing(input_per_1k=1.0, output_per_1k=1.0)}
    cost = calculate_cost(
        "openai", "gpt-4o-mini", prompt_tokens=1000, completion_tokens=1000, overrides=overrides
    )
    assert cost == pytest.approx(2.0)
