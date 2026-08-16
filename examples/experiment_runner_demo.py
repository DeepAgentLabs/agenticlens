from __future__ import annotations

from datetime import datetime, timedelta, timezone

from agenticlens.evaluation import TestCase, TestSuite
from agenticlens.experiments import ExperimentManifest, ExperimentVariant, run_experiment


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
        variants=[
            ExperimentVariant(
                id="baseline",
                name="Baseline",
                target_kind="python",
                target="examples/experiment_runner_demo.py:baseline_target",
            ),
            ExperimentVariant(
                id="cheap-risky",
                name="Cheap but risky",
                target_kind="python",
                target="examples/experiment_runner_demo.py:cheap_risky_target",
            ),
            ExperimentVariant(
                id="slower-quality",
                name="Slower but higher quality",
                target_kind="python",
                target="examples/experiment_runner_demo.py:slower_quality_target",
            ),
        ],
    )

    report = run_experiment(manifest, suite)
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
