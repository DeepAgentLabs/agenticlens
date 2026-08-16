import json
from pathlib import Path

from agenticlens.evaluation import (
    EvaluationContext,
    EvaluatorConfig,
    EvaluatorRegistry,
    LLMJudgeEvaluator,
    Score,
    load_suite,
)
from agenticlens.evaluation import TestCase as EvaluationTestCase
from agenticlens.evaluation import TestSuite as EvaluationTestSuite
from agenticlens.experiments import load_manifest, run_experiment


def _write_target_module(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "from datetime import datetime, timedelta, timezone",
                "",
                "def _result(output, latency_ms, cost):",
                "    started = datetime.now(timezone.utc)",
                "    completed = started + timedelta(milliseconds=latency_ms)",
                "    return {",
                "        'output': output,",
                "        'trace': {",
                "            'application_name': 'experiment-target',",
                "            'started_at': started.isoformat(),",
                "            'completed_at': completed.isoformat(),",
                "            'status': 'succeeded',",
                "            'task_success': output == 'ok',",
                "            'estimated_cost_usd': cost,",
                "            'spans': [],",
                "        },",
                "    }",
                "",
                "def baseline(payload, *, case):",
                "    return _result('ok', 40, 0.001)",
                "",
                "def fast_cheap_bad(payload, *, case):",
                "    return _result('bad', 10, 0.0005)",
                "",
                "def slow_expensive_good(payload, *, case):",
                "    return _result('ok', 120, 0.003)",
            ]
        ),
        encoding="utf-8",
    )


def test_run_experiment_supports_three_variants_and_pareto_summary(tmp_path: Path) -> None:
    target_module = tmp_path / "targets.py"
    suite_file = tmp_path / "suite.json"
    manifest_file = tmp_path / "experiment.json"
    _write_target_module(target_module)
    suite_file.write_text(
        json.dumps(
            {
                "name": "release",
                "version": "1",
                "cases": [{"id": "case-1", "name": "Answer", "expected_output": "ok"}],
            }
        ),
        encoding="utf-8",
    )
    manifest_file.write_text(
        json.dumps(
            {
                "name": "variant-shootout",
                "version": "0.4-draft",
                "baseline_variant_id": "baseline",
                "trial_count": 3,
                "random_seed": 7,
                "variants": [
                    {
                        "id": "baseline",
                        "name": "Baseline",
                        "target_kind": "python",
                        "target": f"{target_module}:baseline",
                    },
                    {
                        "id": "cheap-bad",
                        "name": "Cheap but bad",
                        "target_kind": "python",
                        "target": f"{target_module}:fast_cheap_bad",
                    },
                    {
                        "id": "slow-good",
                        "name": "Slow but good",
                        "target_kind": "python",
                        "target": f"{target_module}:slow_expensive_good",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    report = run_experiment(load_manifest(manifest_file), load_suite(suite_file))

    assert report.trial_count == 3
    assert len(report.variants) == 3
    baseline = next(variant for variant in report.variants if variant.variant_id == "baseline")
    slow_good = next(variant for variant in report.variants if variant.variant_id == "slow-good")
    assert baseline.summary.trial_success_rate == 1.0
    assert slow_good.summary.average_latency_ms.mean > baseline.summary.average_latency_ms.mean
    assert baseline.summary.pass_rate.confidence_interval is not None
    assert "baseline" in report.pareto_frontier_variant_ids
    assert "slow-good" not in report.pareto_frontier_variant_ids
    assert len(report.comparisons) == 2


def test_manifest_requires_at_least_three_variants(tmp_path: Path) -> None:
    manifest_file = tmp_path / "experiment.json"
    manifest_file.write_text(
        json.dumps(
            {
                "name": "too-small",
                "version": "0.4-draft",
                "baseline_variant_id": "baseline",
                "variants": [
                    {
                        "id": "baseline",
                        "name": "Baseline",
                        "target_kind": "python",
                        "target": "module:baseline",
                    },
                    {
                        "id": "candidate",
                        "name": "Candidate",
                        "target_kind": "python",
                        "target": "module:candidate",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    try:
        load_manifest(manifest_file)
    except ValueError as exc:
        assert "at least three variants" in str(exc)
    else:
        raise AssertionError("Expected manifest validation to fail")


def test_run_experiment_preserves_partial_results_after_trial_failure(tmp_path: Path) -> None:
    target_module = tmp_path / "targets.py"
    suite_file = tmp_path / "suite.json"
    manifest_file = tmp_path / "experiment.json"
    counter_file = tmp_path / "counter.txt"
    target_module.write_text(
        "\n".join(
            [
                "from datetime import datetime, timedelta, timezone",
                "",
                f"COUNTER_FILE = {str(counter_file)!r}",
                "",
                "def _count():",
                "    try:",
                "        with open(COUNTER_FILE, 'r', encoding='utf-8') as fh:",
                "            value = int(fh.read().strip() or '0')",
                "    except FileNotFoundError:",
                "        value = 0",
                "    value += 1",
                "    with open(COUNTER_FILE, 'w', encoding='utf-8') as fh:",
                "        fh.write(str(value))",
                "    return value",
                "",
                "def _result(output):",
                "    started = datetime.now(timezone.utc)",
                "    completed = started + timedelta(milliseconds=10)",
                "    return {",
                "        'output': output,",
                "        'trace': {",
                "            'application_name': 'experiment-target',",
                "            'started_at': started.isoformat(),",
                "            'completed_at': completed.isoformat(),",
                "            'status': 'succeeded',",
                "            'task_success': output == 'ok',",
                "            'estimated_cost_usd': 0.001,",
                "            'spans': [],",
                "        },",
                "    }",
                "",
                "def baseline(payload, *, case):",
                "    if _count() == 2:",
                "        raise RuntimeError('transient failure')",
                "    return _result('ok')",
                "",
                "def candidate(payload, *, case):",
                "    return _result('ok')",
                "",
                "def candidate_two(payload, *, case):",
                "    return _result('ok')",
            ]
        ),
        encoding="utf-8",
    )
    suite_file.write_text(
        json.dumps(
            {
                "name": "release",
                "version": "1",
                "cases": [{"id": "case-1", "name": "Answer", "expected_output": "ok"}],
            }
        ),
        encoding="utf-8",
    )
    manifest_file.write_text(
        json.dumps(
            {
                "name": "partial-failure",
                "version": "0.4-draft",
                "baseline_variant_id": "baseline",
                "trial_count": 3,
                "variants": [
                    {
                        "id": "baseline",
                        "name": "Baseline",
                        "target_kind": "python",
                        "target": f"{target_module}:baseline",
                    },
                    {
                        "id": "candidate",
                        "name": "Candidate",
                        "target_kind": "python",
                        "target": f"{target_module}:candidate",
                    },
                    {
                        "id": "candidate-two",
                        "name": "Candidate two",
                        "target_kind": "python",
                        "target": f"{target_module}:candidate_two",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    report = run_experiment(load_manifest(manifest_file), load_suite(suite_file))

    baseline = next(variant for variant in report.variants if variant.variant_id == "baseline")
    assert baseline.summary.attempted_trials == 3
    assert baseline.summary.completed_trials == 2
    assert baseline.summary.failed_trials == 1
    assert baseline.summary.pass_rate is not None
    assert any(trial.status == "failed" for trial in baseline.trials)
    assert len(report.comparisons) == 2


def test_run_experiment_uses_seeded_execution_order(tmp_path: Path) -> None:
    target_module = tmp_path / "targets.py"
    suite_file = tmp_path / "suite.json"
    log_file = tmp_path / "execution.log"
    target_module.write_text(
        "\n".join(
            [
                "from datetime import datetime, timedelta, timezone",
                "",
                f"LOG_FILE = {str(log_file)!r}",
                "",
                "def _record(name):",
                "    with open(LOG_FILE, 'a', encoding='utf-8') as fh:",
                "        fh.write(name + '\\n')",
                "    started = datetime.now(timezone.utc)",
                "    completed = started + timedelta(milliseconds=10)",
                "    return {",
                "        'output': 'ok',",
                "        'trace': {",
                "            'application_name': 'experiment-target',",
                "            'started_at': started.isoformat(),",
                "            'completed_at': completed.isoformat(),",
                "            'status': 'succeeded',",
                "            'task_success': True,",
                "            'estimated_cost_usd': 0.001,",
                "            'spans': [],",
                "        },",
                "    }",
                "",
                "def baseline(payload, *, case):",
                "    return _record('baseline')",
                "",
                "def candidate(payload, *, case):",
                "    return _record('candidate')",
                "",
                "def candidate_two(payload, *, case):",
                "    return _record('candidate-two')",
            ]
        ),
        encoding="utf-8",
    )
    suite_file.write_text(
        json.dumps(
            {
                "name": "release",
                "version": "1",
                "cases": [{"id": "case-1", "name": "Answer", "expected_output": "ok"}],
            }
        ),
        encoding="utf-8",
    )

    manifest = load_manifest(
        _write_manifest(
            tmp_path,
            target_module,
            trial_count=2,
            random_seed=7,
        )
    )
    run_experiment(manifest, load_suite(suite_file))
    first_sequence = log_file.read_text(encoding="utf-8").splitlines()

    log_file.write_text("", encoding="utf-8")
    run_experiment(manifest, load_suite(suite_file))
    second_sequence = log_file.read_text(encoding="utf-8").splitlines()

    assert first_sequence == second_sequence


def test_pareto_frontier_considers_mean_case_pass_rate(tmp_path: Path) -> None:
    target_module = tmp_path / "targets.py"
    suite_file = tmp_path / "suite.json"
    manifest_file = tmp_path / "experiment.json"
    target_module.write_text(
        "\n".join(
            [
                "from datetime import datetime, timedelta, timezone",
                "",
                "def _result(values):",
                "    started = datetime.now(timezone.utc)",
                "    completed = started + timedelta(milliseconds=20)",
                "    return {",
                "        'output': values['output'],",
                "        'trace': {",
                "            'application_name': 'pareto-demo',",
                "            'started_at': started.isoformat(),",
                "            'completed_at': completed.isoformat(),",
                "            'status': 'succeeded',",
                "            'task_success': values['task_success'],",
                "            'estimated_cost_usd': 0.001,",
                "            'spans': [",
                "                {",
                "                    'name': 'demo-model',",
                "                    'span_type': 'model_call',",
                "                    'status': 'succeeded',",
                "                    'estimated_cost_usd': 0.001,",
                "                }",
                "            ],",
                "        },",
                "    }",
                "",
                "def baseline(payload, *, case):",
                "    if case.id == 'case-1':",
                "        return _result({'output': 'ok', 'task_success': False})",
                "    return _result({'output': 'bad', 'task_success': False})",
                "",
                "def candidate(payload, *, case):",
                "    return _result({'output': 'bad', 'task_success': False})",
                "",
                "def candidate_two(payload, *, case):",
                "    if case.id == 'case-1':",
                "        return _result({'output': 'ok', 'task_success': False})",
                "    return _result({'output': 'bad', 'task_success': False})",
            ]
        ),
        encoding="utf-8",
    )
    suite_file.write_text(
        json.dumps(
            {
                "name": "pareto-suite",
                "version": "1",
                "cases": [
                    {"id": "case-1", "name": "Case one", "expected_output": "ok"},
                    {"id": "case-2", "name": "Case two", "expected_output": "ok"},
                ],
            }
        ),
        encoding="utf-8",
    )
    manifest_file.write_text(
        json.dumps(
            {
                "name": "pareto-check",
                "version": "0.4-draft",
                "baseline_variant_id": "baseline",
                "trial_count": 1,
                "variants": [
                    {
                        "id": "baseline",
                        "name": "Baseline",
                        "target_kind": "python",
                        "target": f"{target_module}:baseline",
                    },
                    {
                        "id": "candidate",
                        "name": "Candidate",
                        "target_kind": "python",
                        "target": f"{target_module}:candidate",
                    },
                    {
                        "id": "candidate-two",
                        "name": "Candidate two",
                        "target_kind": "python",
                        "target": f"{target_module}:candidate_two",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    report = run_experiment(load_manifest(manifest_file), load_suite(suite_file))

    assert "candidate-two" in report.pareto_frontier_variant_ids
    assert "candidate" not in report.pareto_frontier_variant_ids


def test_run_experiment_forwards_evaluator_registry(tmp_path: Path) -> None:
    target_module = tmp_path / "judge_targets.py"
    target_module.write_text(
        "\n".join(
            [
                "from datetime import datetime, timedelta, timezone",
                "",
                "def run_case(payload, *, case):",
                "    started = datetime.now(timezone.utc)",
                "    completed = started + timedelta(milliseconds=15)",
                "    return {",
                "        'output': 'ok',",
                "        'trace': {",
                "            'application_name': 'judge-experiment',",
                "            'started_at': started.isoformat(),",
                "            'completed_at': completed.isoformat(),",
                "            'status': 'succeeded',",
                "            'task_success': True,",
                "            'spans': [],",
                "        },",
                "    }",
            ]
        ),
        encoding="utf-8",
    )
    suite = EvaluationTestSuite(
        name="judge-experiment",
        version="1",
        cases=[
            EvaluationTestCase(
                id="case-1",
                name="Judged case",
                evaluators=[EvaluatorConfig(name="quality_judge", threshold=0.8)],
            )
        ],
    )

    def judge(context: EvaluationContext) -> Score:
        return Score(
            name="answer_quality",
            value=0.9,
            passed=False,
            explanation=f"Judge scored {context.sample.case_id}.",
        )

    registry = EvaluatorRegistry()
    registry.register(LLMJudgeEvaluator("quality_judge", judge))

    manifest = load_manifest(
        _manifest_from_inline_targets(
            tmp_path,
            target_module,
            suite_name="judge-experiment",
            baseline_variant_id="baseline",
        )
    )
    report = run_experiment(manifest, suite, registry=registry)

    assert all(variant.summary.failed_trials == 0 for variant in report.variants)
    assert report.variants[0].summary.average_score is not None


def _write_manifest(
    tmp_path: Path,
    target_module: Path,
    *,
    trial_count: int,
    random_seed: int | None,
) -> Path:
    manifest_file = tmp_path / "seeded-experiment.json"
    manifest_file.write_text(
        json.dumps(
            {
                "name": "seeded-order",
                "version": "0.4-draft",
                "baseline_variant_id": "baseline",
                "trial_count": trial_count,
                "random_seed": random_seed,
                "variants": [
                    {
                        "id": "baseline",
                        "name": "Baseline",
                        "target_kind": "python",
                        "target": f"{target_module}:baseline",
                    },
                    {
                        "id": "candidate",
                        "name": "Candidate",
                        "target_kind": "python",
                        "target": f"{target_module}:candidate",
                    },
                    {
                        "id": "candidate-two",
                        "name": "Candidate two",
                        "target_kind": "python",
                        "target": f"{target_module}:candidate_two",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest_file


def _manifest_from_inline_targets(
    tmp_path: Path,
    target_module: Path,
    *,
    suite_name: str,
    baseline_variant_id: str,
) -> Path:
    manifest_file = tmp_path / "tmp-inline-experiment.json"
    manifest_file.write_text(
        json.dumps(
            {
                "name": suite_name,
                "version": "0.4-draft",
                "baseline_variant_id": baseline_variant_id,
                "trial_count": 1,
                "variants": [
                    {
                        "id": "baseline",
                        "name": "Baseline",
                        "target_kind": "python",
                        "target": f"{target_module}:run_case",
                    },
                    {
                        "id": "candidate",
                        "name": "Candidate",
                        "target_kind": "python",
                        "target": f"{target_module}:run_case",
                    },
                    {
                        "id": "candidate-two",
                        "name": "Candidate two",
                        "target_kind": "python",
                        "target": f"{target_module}:run_case",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest_file
