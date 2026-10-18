"""ModelFit config validation and constraint overrides."""

import pytest
from pydantic import ValidationError

from agenticlens.modelfit import (
    ModelCandidate,
    ModelConstraints,
    ModelFitConfig,
    ScoringWeights,
    TaskCategory,
)


def test_category_overrides_replace_only_the_fields_they_set() -> None:
    defaults = ModelConstraints(min_pass_rate=0.9, max_cost_per_case_usd=0.01)
    override = ModelConstraints(max_cost_per_case_usd=0.002)

    merged = defaults.merged(override)

    assert merged.min_pass_rate == 0.9
    assert merged.max_cost_per_case_usd == 0.002
    assert defaults.max_cost_per_case_usd == 0.01


def test_an_explicit_null_override_removes_a_default_limit() -> None:
    defaults = ModelConstraints(min_safety_pass_rate=1.0)
    override = ModelConstraints.model_validate({"min_safety_pass_rate": None})

    assert defaults.merged(override).min_safety_pass_rate is None
    assert defaults.merged(None) == defaults


def test_weights_must_not_all_be_zero() -> None:
    with pytest.raises(ValidationError, match="at least one scoring weight"):
        ScoringWeights(quality=0, cost=0, latency=0, reliability=0)


def test_categories_need_a_case_selector() -> None:
    with pytest.raises(ValidationError, match="needs at least one of tags"):
        TaskCategory(id="empty")
    assert TaskCategory(id="policy", tags=["policy"]).display_name == "policy"
    assert TaskCategory(id="policy", name="Policy", tags=["policy"]).display_name == "Policy"


def test_category_ids_must_be_slug_like() -> None:
    with pytest.raises(ValidationError):
        TaskCategory(id="has space", tags=["x"])


def test_config_rejects_duplicate_categories_and_candidates() -> None:
    with pytest.raises(ValidationError, match="category IDs must be unique"):
        ModelFitConfig(
            categories=[TaskCategory(id="a", tags=["a"]), TaskCategory(id="a", tags=["b"])]
        )
    with pytest.raises(ValidationError, match="candidate variant IDs must be unique"):
        ModelFitConfig(candidates=[ModelCandidate(variant_id="x"), ModelCandidate(variant_id="x")])


def test_all_is_reserved_while_the_overall_category_is_enabled() -> None:
    with pytest.raises(ValidationError, match="reserved"):
        ModelFitConfig(categories=[TaskCategory(id="all", tags=["x"])])
    config = ModelFitConfig(include_overall=False, categories=[TaskCategory(id="all")])
    assert config.categories[0].id == "all"


def test_list_constraints_accept_null_overrides() -> None:
    defaults = ModelConstraints(blocked_providers=["x"], required_capabilities=["pii_ok"])
    override = ModelConstraints.model_validate(
        {"blocked_providers": None, "required_capabilities": None}
    )

    merged = defaults.merged(override)

    assert merged.blocked_providers is None and merged.required_capabilities is None
