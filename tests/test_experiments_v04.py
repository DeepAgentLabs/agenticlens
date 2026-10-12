import csv
import io
import json
from pathlib import Path
from typing import Any

import pytest

from agenticlens.evaluation import TestCase as EvalCase
from agenticlens.evaluation import TestSuite as EvalSuite
from agenticlens.experiments import (
    ExperimentManifest,
    ExperimentReport,
    load_manifest,
    load_recorded_trials,
    render_case_matrix_csv,
    render_experiment_html,
    render_variant_csv,
    run_experiment,
)

SUITE = EvalSuite(
    name="support",
    version="2",
    cases=[
        EvalCase(id="refund", name="Refund", expected_output="ok"),
        EvalCase(id="billing", name="Billing", expected_output="ok"),
    ],
)


def _trial(outputs: dict[str, str], *, latency: float, cost: float | None) -> dict[str, Any]:
    return {
        "samples": [
            {
                "case_id": case_id,
                "output": output,
                "trace": {
                    "trace_id": f"{case_id}-{output}",
                    "total_latency_ms": latency,
                    "estimated_cost_usd": cost,
                    "cost_source": "measured" if cost is not None else None,
                },
            }
            for case_id, output in outputs.items()
        ]
    }


def _write(path: Path, trials: list[dict[str, Any]]) -> str:
    path.write_text(json.dumps({"trials": trials}), encoding="utf-8")
    return path.name


def _manifest(tmp_path: Path, *, trial_count: int = 4, **extra: Any) -> Path:
    good = [_trial({"refund": "ok", "billing": "ok"}, latency=40, cost=0.002)] * 4
    # Flaky on billing: passes in trials 1 and 3 only.
    flaky = [
        _trial({"refund": "ok", "billing": "ok" if i % 2 == 0 else "no"}, latency=20, cost=0.001)
        for i in range(4)
    ]
    bad = [_trial({"refund": "no", "billing": "no"}, latency=10, cost=0.0005)] * 4
    manifest = {
        "name": "model-and-prompt",
        "version": "1",
        "baseline_variant_id": "baseline",
        "trial_count": trial_count,
        "random_seed": 3,
        "minimum_trials": 4,
        "variants": [
            {
                "id": "baseline",
                "name": "Baseline",
                "target_kind": "recorded",
                "target": _write(tmp_path / "baseline.json", good),
                "factors": {"model": "large", "prompt": "v1"},
            },
            {
                "id": "small-model",
                "name": "Small model",
                "target_kind": "recorded",
                "target": _write(tmp_path / "small.json", flaky),
                "factors": {"model": "small", "prompt": "v1"},
            },
            {
                "id": "terse-prompt",
                "name": "Terse prompt",
                "target_kind": "recorded",
                "target": _write(tmp_path / "terse.json", bad),
                "factors": {"model": "large", "prompt": "v2-terse"},
            },
        ],
        **extra,
    }
    path = tmp_path / "experiment.yaml"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def _variant(report: ExperimentReport, variant_id: str) -> Any:
    return next(v for v in report.variants if v.variant_id == variant_id)


def test_recorded_targets_resolve_relative_to_the_manifest(tmp_path: Path) -> None:
    manifest = load_manifest(_manifest(tmp_path))
    assert all(
        Path(v.target).is_absolute() or v.target.startswith(str(tmp_path))
        for v in manifest.variants
    )


def test_per_case_pass_at_k_and_consistency(tmp_path: Path) -> None:
    report = run_experiment(load_manifest(_manifest(tmp_path)), SUITE)

    assert report.pass_k == [1, 4]
    small = _variant(report, "small-model")
    billing = next(case for case in small.cases if case.case_id == "billing")
    assert (billing.attempts, billing.passes) == (4, 2)
    assert billing.pass_at_k == {"1": 0.5, "4": 1.0}
    assert billing.pass_hat_k == {"1": 0.5, "4": 0.0}
    assert not billing.consistent
    assert small.summary.flaky_case_ids == ["billing"]
    assert small.summary.consistency_rate == 0.5
    # Variant pass@k averages the cases: refund always passes.
    assert small.summary.pass_at_k["1"] == pytest.approx(0.75)
    assert small.summary.pass_hat_k["4"] == pytest.approx(0.5)
    assert small.summary.case_pass_rate == pytest.approx(6 / 8)
    assert small.summary.case_pass_rate_interval is not None
    assert small.summary.case_pass_rate_interval.method == "wilson"


def test_comparisons_name_changed_factors_and_significance(tmp_path: Path) -> None:
    report = run_experiment(load_manifest(_manifest(tmp_path)), SUITE)

    by_candidate = {c.candidate_variant_id: c for c in report.comparisons}
    terse = by_candidate["terse-prompt"]
    assert terse.changed_factors == {"prompt": ["v1", "v2-terse"]}
    assert terse.case_pass_rate_delta == pytest.approx(-1.0)
    assert terse.statistically_significant is True
    assert sorted(terse.regressed_case_ids) == ["billing", "refund"]
    assert terse.pass_rate_delta.regressed

    small = by_candidate["small-model"]
    assert small.changed_factors == {"model": ["large", "small"]}
    assert small.regressed_case_ids == ["billing"]
    assert small.statistically_significant is False  # 8/8 vs 6/8 is not enough evidence


def test_factor_levels_group_variants(tmp_path: Path) -> None:
    report = run_experiment(load_manifest(_manifest(tmp_path)), SUITE)

    levels = {(level.factor, level.value): level for level in report.factor_levels}
    assert levels[("model", "large")].variant_ids == ["baseline", "terse-prompt"]
    assert levels[("model", "large")].mean_pass_rate == pytest.approx(0.5)
    assert levels[("prompt", "v1")].mean_pass_rate == pytest.approx(0.875)
    assert levels[("model", "small")].mean_cost_usd == pytest.approx(0.002)


def test_randomization_and_settings_are_recorded(tmp_path: Path) -> None:
    manifest = load_manifest(_manifest(tmp_path))
    first = run_experiment(manifest, SUITE, confidence_level=0.9, regression_threshold=0.1)
    second = run_experiment(manifest, SUITE)

    assert first.randomization is not None and first.randomization.shuffled
    assert first.randomization.random_seed == 3
    assert len(first.randomization.execution_order) == 12
    assert first.randomization.execution_order == second.randomization.execution_order
    assert (first.confidence_level, first.regression_threshold) == (0.9, 0.1)
    assert first.case_ids == ["refund", "billing"]


def test_minimum_sample_warnings(tmp_path: Path) -> None:
    report = run_experiment(load_manifest(_manifest(tmp_path, trial_count=2)), SUITE)

    assert any("fewer than 4" in warning for warning in report.warnings)
    assert all(
        any("exploratory" in warning for warning in comparison.warnings)
        for comparison in report.comparisons
    )


def test_missing_recorded_trial_fails_only_that_trial(tmp_path: Path) -> None:
    path = _manifest(tmp_path)
    data = json.loads(path.read_text())
    data["trial_count"] = 5
    path.write_text(json.dumps(data))

    report = run_experiment(load_manifest(path), SUITE)

    baseline = _variant(report, "baseline")
    assert baseline.summary.failed_trials == 1
    assert "trial 5 is missing" in (baseline.trials[-1].error_message or "")
    # The failed trial counts as a failed attempt on every case.
    assert baseline.cases[0].attempts == 5 and baseline.cases[0].passes == 4


def test_multiple_changed_factors_are_flagged(tmp_path: Path) -> None:
    path = _manifest(tmp_path)
    data = json.loads(path.read_text())
    data["variants"][2]["factors"] = {"model": "small", "prompt": "v2-terse"}
    path.write_text(json.dumps(data))

    report = run_experiment(load_manifest(path), SUITE)

    terse = next(c for c in report.comparisons if c.candidate_variant_id == "terse-prompt")
    assert any("cannot be attributed" in warning for warning in terse.warnings)


def test_pass_k_must_fit_trial_count() -> None:
    with pytest.raises(ValueError, match="pass_k"):
        ExperimentManifest(
            name="x",
            version="1",
            baseline_variant_id="a",
            trial_count=2,
            pass_k=[3],
            variants=[
                {"id": i, "name": i, "target_kind": "recorded", "target": "t.json"}
                for i in ("a", "b", "c")
            ],
        )


def test_recorded_file_validation(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"trials": []}))
    with pytest.raises(ValueError, match="non-empty"):
        load_recorded_trials(empty)
    nested = tmp_path / "list.json"
    nested.write_text(json.dumps({"trials": [[{"case_id": "a", "output": "x", "trace": {}}]]}))
    assert load_recorded_trials(nested)[0][0].case_id == "a"


def test_html_report_shows_all_dimensions_and_heatmap(tmp_path: Path) -> None:
    report = run_experiment(load_manifest(_manifest(tmp_path)), SUITE)

    html = render_experiment_html(report)

    for text in (
        "Quality, cost, latency, and reliability",
        "pass@4",
        "pass^4",
        "Test-level heatmap",
        "flaky",
        "prompt: v1 → v2-terse",
        "Factor levels",
        "Execution order",
        "prefers-color-scheme: dark",
    ):
        assert text in html
    assert "<script" not in html and "http://" not in html.split("</style>")[1]


def test_html_escapes_user_supplied_names(tmp_path: Path) -> None:
    path = _manifest(tmp_path)
    data = json.loads(path.read_text())
    data["variants"][1]["name"] = "<script>alert(1)</script>"
    path.write_text(json.dumps(data))

    html = render_experiment_html(run_experiment(load_manifest(path), SUITE))

    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_csv_exports(tmp_path: Path) -> None:
    report = run_experiment(load_manifest(_manifest(tmp_path)), SUITE)

    variants = list(csv.DictReader(io.StringIO(render_variant_csv(report))))
    cases = list(csv.DictReader(io.StringIO(render_case_matrix_csv(report))))

    assert [row["variant_id"] for row in variants] == ["baseline", "small-model", "terse-prompt"]
    small = variants[1]
    assert small["factors"] == "model=small;prompt=v1"
    assert float(small["pass_at_1"]) == pytest.approx(0.75)
    assert small["changed_factors"] == "model=large->small"
    assert variants[0]["case_pass_rate_delta"] == ""  # baseline has no comparison
    assert len(cases) == 6
    billing = next(
        r for r in cases if r["variant_id"] == "small-model" and r["case_id"] == "billing"
    )
    assert billing["passes"] == "2" and billing["consistent"] == "False"


def test_report_round_trips_through_json(tmp_path: Path) -> None:
    report = run_experiment(load_manifest(_manifest(tmp_path)), SUITE)
    restored = ExperimentReport.model_validate_json(report.model_dump_json())
    assert restored == report


def test_live_python_variants_run_cases_concurrently(tmp_path: Path) -> None:
    target = tmp_path / "targets.py"
    target.write_text(
        "\n".join(
            [
                "def run(payload, *, case):",
                "    trace = {'trace_id': case.id, 'total_latency_ms': 5}",
                "    return {'output': 'ok', 'trace': trace}",
            ]
        ),
        encoding="utf-8",
    )
    manifest = ExperimentManifest(
        name="live",
        version="1",
        baseline_variant_id="a",
        trial_count=2,
        max_workers=2,
        variants=[
            {"id": i, "name": i, "target_kind": "python", "target": f"{target}:run"}
            for i in ("a", "b", "c")
        ],
    )

    report = run_experiment(manifest, SUITE)

    assert all(v.summary.case_pass_rate == 1.0 for v in report.variants)
    assert report.randomization is not None and not report.randomization.shuffled
