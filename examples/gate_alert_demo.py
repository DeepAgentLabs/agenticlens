"""Cooldown-protected release-gate alerts.

Runs the gate three times against a failing report. The first run sends one
alert; the second, ten minutes later, is suppressed by the one-hour cooldown;
the third, after the cooldown, alerts again. A print-only sender stands in
for the webhook, so nothing leaves the machine.

    python examples/gate_alert_demo.py

From CI, the CLI does the same with a real webhook:

    agenticlens gate agenticlens-evaluation.json --min-pass-rate 0.95 \\
      --notify-webhook "$SLACK_WEBHOOK_URL" --notify-format slack \\
      --cooldown-minutes 60 --notify-state .agenticlens/gate-notifications.json
"""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agenticlens.evaluation import (
    EvalTrace,
    EvaluationSample,
    GateConfig,
    TestCase,
    TestSuite,
    evaluate_gate,
    evaluate_suite,
    notify_gate_breach,
)


def print_sender(url: str, payload: dict[str, Any], timeout: float) -> None:
    print(f"  -> POST {url}\n     {json.dumps(payload)}")


def main() -> None:
    suite = TestSuite(
        name="nightly-support",
        version="7",
        cases=[TestCase(id=str(i), name=f"case {i}", expected_output="ok") for i in range(4)],
    )
    samples = [
        EvaluationSample(
            case_id=str(i),
            output="ok" if i < 3 else "wrong",
            trace=EvalTrace(trace_id=f"t{i}", estimated_cost_usd=0.05, cost_source="measured"),
        )
        for i in range(4)
    ]
    report = evaluate_suite(suite, samples)
    config = GateConfig(min_pass_rate=0.95, max_total_cost_usd=0.1)
    decision = evaluate_gate(report, config)
    print(f"Gate passed: {decision.passed}; reasons: {decision.reasons}")

    start = datetime(2026, 10, 12, 2, 0, tzinfo=timezone.utc)
    with tempfile.TemporaryDirectory() as directory:
        state = Path(directory) / "gate-notifications.json"
        for minutes in (0, 10, 70):
            print(f"\nRun at +{minutes} min:")
            result = notify_gate_breach(
                report,
                decision,
                config,
                url="https://hooks.slack.com/services/EXAMPLE",
                webhook_format="slack",
                cooldown=timedelta(hours=1),
                state_path=state,
                now=start + timedelta(minutes=minutes),
                sender=print_sender,
            )
            print(
                f"  sent={result.sent} notified={result.notified_keys} "
                f"suppressed={result.suppressed_keys}"
            )


if __name__ == "__main__":
    main()
