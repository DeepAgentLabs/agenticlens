"""Build small recorded experiment reports with exact per-case outcomes for ModelFit tests."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from agenticlens.experiments import (
    ExperimentManifest,
    ExperimentReport,
    ExperimentTrialResult,
    ExperimentVariant,
    load_experiment_suite,
    run_experiment,
)

DEFAULT_CASES = {
    "p1": ["policy"],
    "p2": ["policy"],
    "o1": ["orders"],
    "s1": ["safety"],
}


@dataclass
class Spec:
    """One variant: per-case pass/fail per trial, a flat cost per case, and latency."""

    outcomes: dict[str, list[bool]]
    cost: float | None = 0.001
    latency: float = 1000.0
    factors: dict[str, str] = field(default_factory=dict)


def passes(n_pass: int, n_fail: int = 0) -> list[bool]:
    return [True] * n_pass + [False] * n_fail


def build_report(
    tmp_path: Path,
    specs: dict[str, Spec],
    *,
    cases: dict[str, list[str]] | None = None,
    baseline: str | None = None,
    name: str = "modelfit-test",
    domains: dict[str, str] | None = None,
) -> ExperimentReport:
    cases = cases or DEFAULT_CASES
    domains = domains or {}
    trial_counts = {len(outcome) for spec in specs.values() for outcome in spec.outcomes.values()}
    assert len(trial_counts) == 1, "every case needs the same number of trials"
    trials = trial_counts.pop()
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    suite = {
        "name": f"{name}-suite",
        "version": "1.0",
        "cases": [
            {
                "id": case_id,
                "name": case_id,
                "input": {"q": case_id},
                "expected_contains": ["ok"],
                "tags": tags,
                "metadata": {"domain": domains[case_id]} if case_id in domains else {},
            }
            for case_id, tags in cases.items()
        ],
    }
    (root / "suite.json").write_text(json.dumps(suite), encoding="utf-8")
    variants = []
    for variant_id, spec in specs.items():
        recorded = []
        for trial in range(trials):
            samples = []
            for case_id in cases:
                trace: dict[str, object] = {
                    "trace_id": f"{variant_id}-{trial}-{case_id}",
                    "total_latency_ms": spec.latency + trial,
                }
                if spec.cost is not None:
                    trace["estimated_cost_usd"] = spec.cost
                    trace["cost_source"] = "estimated"
                samples.append(
                    {
                        "case_id": case_id,
                        "output": "ok" if spec.outcomes[case_id][trial] else "no",
                        "trace": trace,
                    }
                )
            recorded.append({"samples": samples})
        path = root / f"{variant_id}.json"
        path.write_text(json.dumps({"trials": recorded}), encoding="utf-8")
        variants.append(
            ExperimentVariant(
                id=variant_id,
                name=variant_id,
                target_kind="recorded",
                target=str(path),
                factors=spec.factors or {"model": variant_id},
            )
        )
    manifest = ExperimentManifest(
        name=name,
        version="1",
        baseline_variant_id=baseline or next(iter(specs)),
        trial_count=trials,
        minimum_trials=1,
        variants=variants,
    )
    return run_experiment(manifest, load_experiment_suite(root / "suite.json"))


def fail_trial(report: ExperimentReport, variant_id: str, trial_index: int) -> ExperimentReport:
    """Replace one trial of a variant with a failed (no report) trial."""
    variants = []
    for variant in report.variants:
        if variant.variant_id == variant_id:
            trials = [
                ExperimentTrialResult(
                    trial_index=trial.trial_index, status="failed", error_message="boom"
                )
                if trial.trial_index == trial_index
                else trial
                for trial in variant.trials
            ]
            variant = variant.model_copy(update={"trials": trials})
        variants.append(variant)
    return report.model_copy(update={"variants": variants})


def uniform(
    case_ids: list[str] | dict[str, list[str]], outcome: list[bool]
) -> dict[str, list[bool]]:
    return {case_id: list(outcome) for case_id in case_ids}
