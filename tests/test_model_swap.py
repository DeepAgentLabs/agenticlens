from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from agenticlens.config.live_pricing import LivePricingConfig
from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity, StepType
from agenticlens.models.metrics import Metrics
from agenticlens.models.step import Step
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.model_swap import ModelSwapRecommender

_DEFAULT_CONFIG = RecommenderConfig()


def _workflow_with_step(
    provider: str | None, model: str | None, **metric_kwargs: object
) -> Workflow:
    workflow = Workflow(name="Test", start_time=datetime.now(timezone.utc))
    workflow.steps.append(
        Step(
            name="LLM Call",
            type=StepType.LLM_CALL,
            provider=provider,
            model=model,
            metrics=Metrics(**metric_kwargs),
        )
    )
    return workflow


def test_recommends_cheapest_static_candidate_when_no_live_pricing() -> None:
    workflow = _workflow_with_step(
        "anthropic", "claude-3-5-sonnet", prompt_tokens=1000, completion_tokens=1000
    )
    recs = ModelSwapRecommender().evaluate(workflow, _DEFAULT_CONFIG)

    assert len(recs) == 1
    rec = recs[0]
    assert rec.title == "Cheaper model available"
    assert "openai:gpt-4o-mini" in rec.description
    assert rec.severity == Severity.WARNING
    assert rec.cost_savings == pytest.approx(0.018 - 0.00075)


def test_no_recommendation_when_already_cheapest() -> None:
    workflow = _workflow_with_step(
        "openai", "gpt-4o-mini", prompt_tokens=1000, completion_tokens=1000
    )
    recs = ModelSwapRecommender().evaluate(workflow, _DEFAULT_CONFIG)

    assert recs == []


def test_no_recommendation_below_savings_threshold() -> None:
    # claude-3-5-haiku -> gpt-4o-mini is ~84% cheaper; a 90% floor should suppress it.
    workflow = _workflow_with_step(
        "anthropic", "claude-3-5-haiku", prompt_tokens=1000, completion_tokens=1000
    )
    config = RecommenderConfig(model_swap_min_savings_pct=90.0)
    recs = ModelSwapRecommender().evaluate(workflow, config)

    assert recs == []


def test_skips_step_with_unknown_current_pricing_and_does_not_warn(
    recwarn: pytest.WarningsRecorder,
) -> None:
    workflow = _workflow_with_step(
        "openai", "not-a-real-model", prompt_tokens=1000, completion_tokens=1000
    )
    recs = ModelSwapRecommender().evaluate(workflow, _DEFAULT_CONFIG)

    assert recs == []
    assert len(recwarn.list) == 0


def test_skips_step_with_no_provider_or_model() -> None:
    workflow = _workflow_with_step(None, None, prompt_tokens=1000, completion_tokens=1000)
    recs = ModelSwapRecommender().evaluate(workflow, _DEFAULT_CONFIG)

    assert recs == []


def test_skips_step_with_zero_tokens() -> None:
    workflow = _workflow_with_step(
        "anthropic", "claude-3-5-sonnet", prompt_tokens=0, completion_tokens=0
    )
    recs = ModelSwapRecommender().evaluate(workflow, _DEFAULT_CONFIG)

    assert recs == []


def test_explicit_candidate_list_is_respected() -> None:
    workflow = _workflow_with_step(
        "anthropic", "claude-3-5-sonnet", prompt_tokens=1000, completion_tokens=1000
    )
    recommender = ModelSwapRecommender(candidates=["anthropic:claude-3-5-haiku"])
    recs = recommender.evaluate(workflow, _DEFAULT_CONFIG)

    assert len(recs) == 1
    assert "anthropic:claude-3-5-haiku" in recs[0].description


_FAKE_LIVE_TABLE = {
    "gpt-4o-mini": {
        "litellm_provider": "openai",
        "mode": "chat",
        "input_cost_per_token": 1.5e-7,
        "output_cost_per_token": 6e-7,
        "max_input_tokens": 128000,
    },
    "tiny-context-model": {
        "litellm_provider": "openai",
        "mode": "chat",
        "input_cost_per_token": 1e-9,
        "output_cost_per_token": 1e-9,
        "max_input_tokens": 10,
    },
    "ft:gpt-4o-mini-custom": {
        "litellm_provider": "openai",
        "mode": "chat",
        "input_cost_per_token": 1e-10,
        "output_cost_per_token": 1e-10,
        "max_input_tokens": 128000,
    },
    "text-embedding-3-small": {
        "litellm_provider": "openai",
        "mode": "embedding",
        "input_cost_per_token": 1e-10,
        "output_cost_per_token": 0,
    },
    "bedrock/anthropic.claude-3-5-sonnet": {
        "litellm_provider": "bedrock",
        "mode": "chat",
        "input_cost_per_token": 1e-10,
        "output_cost_per_token": 1e-10,
        "max_input_tokens": 200000,
    },
}


def test_live_feed_candidates_filter_ft_mode_provider_and_context_window() -> None:
    workflow = _workflow_with_step("openai", "gpt-4o", prompt_tokens=1000, completion_tokens=500)
    live_pricing = LivePricingConfig(enabled=True)
    recommender = ModelSwapRecommender(live_pricing=live_pricing)

    with patch(
        "agenticlens.recommenders.model_swap.get_live_pricing_table",
        return_value=_FAKE_LIVE_TABLE,
    ):
        recs = recommender.evaluate(workflow, _DEFAULT_CONFIG)

    assert len(recs) == 1
    rec = recs[0]
    # Only "gpt-4o-mini" should have survived: the ft: entry, the embedding
    # entry, the non-allowlisted bedrock entry, and the context-window-limited
    # tiny-context-model are all excluded despite being cheaper on paper.
    assert "openai:gpt-4o-mini" in rec.description
    assert "tiny-context-model" not in rec.description
    assert "ft:" not in rec.description
    assert "bedrock" not in rec.description
