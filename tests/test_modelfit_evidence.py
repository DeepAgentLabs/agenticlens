"""Experiment reports become per-candidate, per-case attempt evidence."""

import hashlib
from pathlib import Path

import pytest

from agenticlens.modelfit import (
    ModelCandidate,
    ModelFitConfig,
    collect_candidates,
    load_experiment_evidence,
)
from agenticlens.modelfit.evidence import ExperimentEvidence
from modelfit_support import DEFAULT_CASES, Spec, build_report, fail_trial, passes, uniform


def _three(tmp_path: Path, name: str = "exp", **extra: Spec):
    specs = {
        "a": Spec(uniform(DEFAULT_CASES, passes(3))),
        "b": Spec(uniform(DEFAULT_CASES, passes(2, 1))),
        "c": Spec(uniform(DEFAULT_CASES, passes(1, 2))),
        **extra,
    }
    return build_report(tmp_path, specs, name=name)


def test_every_trial_contributes_one_attempt_per_case(tmp_path: Path) -> None:
    report = _three(tmp_path)
    candidates, warnings = collect_candidates([ExperimentEvidence(report)], ModelFitConfig())

    assert [c.variant.variant_id for c in candidates] == ["a", "b", "c"]
    b = candidates[1]
    assert set(b.cases) == set(DEFAULT_CASES)
    attempts = b.cases["p1"].attempts
    assert [a.passed for a in attempts] == [True, True, False]
    assert all(a.completed and a.cost_usd == 0.001 for a in attempts)
    assert b.cases["s1"].tags == ["safety"]
    assert warnings == []


def test_failed_trials_count_as_failed_attempts_without_cost(tmp_path: Path) -> None:
    report = fail_trial(_three(tmp_path), "a", 2)
    candidates, _ = collect_candidates([ExperimentEvidence(report)], ModelFitConfig())

    attempts = candidates[0].cases["p1"].attempts
    assert [(a.passed, a.completed) for a in attempts] == [
        (True, True),
        (False, False),
        (True, True),
    ]
    assert attempts[1].cost_usd is None and attempts[1].latency_ms is None


def test_identity_prefers_catalog_then_factor_then_metadata(tmp_path: Path) -> None:
    report = _three(tmp_path)
    config = ModelFitConfig(
        candidates=[
            ModelCandidate(
                variant_id="a", model="catalog-model", provider="p-a", capabilities=["x"]
            )
        ]
    )
    metadata = {"b": {"provider": "p-b", "deployment": "on_prem", "capabilities": "tools, pii"}}
    candidates, _ = collect_candidates([ExperimentEvidence(report)], config, metadata)

    a, b, c = candidates
    assert (a.model, a.provider, a.capabilities) == ("catalog-model", "p-a", ["x"])
    assert (b.model, b.provider, b.deployment, b.capabilities) == (
        "b",
        "p-b",
        "on_prem",
        ["tools", "pii"],
    )
    assert (c.model, c.provider, c.deployment) == ("c", None, None)


def test_excluded_variants_are_skipped_and_unknown_catalog_entries_warned(tmp_path: Path) -> None:
    report = _three(tmp_path)
    config = ModelFitConfig(
        exclude_variant_ids=["c"], candidates=[ModelCandidate(variant_id="ghost")]
    )
    candidates, warnings = collect_candidates([ExperimentEvidence(report)], config)

    assert [c.variant.variant_id for c in candidates] == ["a", "b"]
    assert any("ghost" in warning for warning in warnings)


def test_duplicate_variant_ids_across_reports_are_refused(tmp_path: Path) -> None:
    first = _three(tmp_path, "one")
    second = _three(tmp_path, "two")
    with pytest.raises(ValueError, match="more than one experiment report"):
        collect_candidates(
            [ExperimentEvidence(first), ExperimentEvidence(second)], ModelFitConfig()
        )


def test_mixed_suites_and_shared_models_are_warned(tmp_path: Path) -> None:
    first = _three(tmp_path, "one")
    second = build_report(
        tmp_path,
        {
            "d": Spec(uniform(DEFAULT_CASES, passes(3)), factors={"model": "a"}),
            "e": Spec(uniform(DEFAULT_CASES, passes(3))),
            "f": Spec(uniform(DEFAULT_CASES, passes(3))),
        },
        name="two",
    )
    _, warnings = collect_candidates(
        [ExperimentEvidence(first), ExperimentEvidence(second)], ModelFitConfig()
    )

    assert any("different suites" in warning for warning in warnings)
    assert any("Variants a, d share model 'a'" in warning for warning in warnings)


def test_loading_from_a_file_fingerprints_its_bytes(tmp_path: Path) -> None:
    report = _three(tmp_path)
    path = tmp_path / "experiment.json"
    path.write_text(report.model_dump_json(), encoding="utf-8")

    evidence = load_experiment_evidence(path)

    assert evidence.file == "experiment.json"
    assert evidence.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    assert evidence.report.experiment_name == report.experiment_name
