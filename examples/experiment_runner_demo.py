"""Run a live three-variant experiment against Python targets in this file.

Each variant names the factor it changes (`model`, `prompt`), so the report
attributes each baseline delta to that factor. Writes JSON, HTML, and CSV
reports to examples/artifacts/.

    python examples/experiment_runner_demo.py

For a replay of saved results (no agent calls at all), see
examples/experiments/run_recorded_experiment.py.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from agenticlens.evaluation import TestCase, TestSuite
from agenticlens.experiments import (
    ExperimentManifest,
    ExperimentVariant,
    run_experiment,
    save_case_matrix_csv,
    save_experiment_html,
    save_variant_csv,
)

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"


def _result(*, output: str, latency_ms: float, cost: float) -> dict[str, object]:
    started = datetime.now(timezone.utc)
    completed = started + timedelta(milliseconds=latency_ms)
    return {
        "output": output,
        "trace": {
            "application_name": "experiment-runner-demo",
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat(),
            "status": "succeeded",
            "task_success": output == "ok",
            "spans": [
                {
                    "name": "experiment-model-call",
                    "span_type": "model_call",
                    "started_at": started.isoformat(),
                    "completed_at": completed.isoformat(),
                    "latency_ms": latency_ms,
                    "status": "succeeded",
                    "estimated_cost_usd": cost,
                }
            ],
        },
    }


def baseline_target(payload, *, case):
    return _result(output="ok", latency_ms=45, cost=0.0015)


def cheap_risky_target(payload, *, case):
    return _result(output="bad", latency_ms=18, cost=0.0007)


def slower_quality_target(payload, *, case):
    return _result(output="ok", latency_ms=90, cost=0.0024)


def main() -> None:
    suite = TestSuite(
        name="experiment-demo-suite",
        version="1.0",
        cases=[
            TestCase(
                id="answer-1",
                name="Answer must equal ok",
                input={"prompt": "demo"},
                expected_output="ok",
            )
        ],
    )
    manifest = ExperimentManifest(
        name="variant-shootout-demo",
        version="0.4-draft",
        baseline_variant_id="baseline",
        trial_count=3,
        random_seed=11,
        minimum_trials=3,
        variants=[
            ExperimentVariant(
                id="baseline",
                name="Baseline",
                target_kind="python",
                target=f"{Path(__file__).resolve()}:baseline_target",
                factors={"model": "large", "prompt": "v1"},
            ),
            ExperimentVariant(
                id="cheap-risky",
                name="Cheap but risky",
                target_kind="python",
                target=f"{Path(__file__).resolve()}:cheap_risky_target",
                factors={"model": "small", "prompt": "v1"},
            ),
            ExperimentVariant(
                id="slower-quality",
                name="Slower but higher quality",
                target_kind="python",
                target=f"{Path(__file__).resolve()}:slower_quality_target",
                factors={"model": "large", "prompt": "v2-detailed"},
            ),
        ],
    )

    report = run_experiment(manifest, suite)
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / "experiment-demo.json").write_text(report.model_dump_json(indent=2))
    save_experiment_html(report, ARTIFACTS / "experiment-demo.html")
    save_variant_csv(report, ARTIFACTS / "experiment-demo-variants.csv")
    save_case_matrix_csv(report, ARTIFACTS / "experiment-demo-cases.csv")

    for variant in report.variants:
        summary = variant.summary
        print(
            f"{variant.variant_id:16} pass rate {summary.case_pass_rate:.0%}  "
            f"pass^3 {summary.pass_hat_k.get('3', 0):.0%}  "
            f"pareto={'yes' if variant.pareto_optimal else 'no'}"
        )
    for comparison in report.comparisons:
        print(f"{comparison.candidate_variant_id}: changed {comparison.changed_factors}")
    print(f"Reports written to {ARTIFACTS}")


if __name__ == "__main__":
    main()
