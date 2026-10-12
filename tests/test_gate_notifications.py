import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from agenticlens.evaluation import (
    CaseEvaluation,
    EvaluationReport,
    EvaluationSummary,
    GateConfig,
    breached_thresholds,
    evaluate_gate,
    notify_gate_breach,
)

NOW = datetime(2026, 10, 12, 9, 0, tzinfo=timezone.utc)


def _report(*, pass_rate: float = 0.5, cost: float | None = 0.4) -> EvaluationReport:
    return EvaluationReport(
        suite_name="nightly",
        suite_version="3",
        summary=EvaluationSummary(
            total_cases=2,
            passed_cases=round(pass_rate * 2),
            failed_cases=2 - round(pass_rate * 2),
            pass_rate=pass_rate,
            average_score=pass_rate,
            total_cost_usd=cost,
            average_latency_ms=120,
        ),
        cases=[
            CaseEvaluation(
                case_id=str(i),
                case_name=str(i),
                passed=True,
                scores=[],
                output="",
                trace_id=f"t{i}",
                latency_ms=120,
                cost_usd=None if cost is None else cost / 2,
            )
            for i in range(2)
        ],
    )


CONFIG = GateConfig(min_pass_rate=0.9, max_total_cost_usd=0.1, max_average_latency_ms=500)


class Recorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def __call__(self, url: str, payload: dict[str, Any], timeout: float) -> None:
        self.calls.append((url, payload))


def test_breaches_are_keyed_by_threshold_and_category() -> None:
    decision = evaluate_gate(_report(), CONFIG)

    breaches = {b.key: b.category for b in breached_thresholds(decision, CONFIG)}

    assert breaches == {"pass_rate": "quality", "total_cost_usd": "budget"}


def test_unavailable_cost_counts_as_a_budget_breach() -> None:
    decision = evaluate_gate(_report(cost=None), CONFIG)
    keys = [b.key for b in breached_thresholds(decision, CONFIG)]
    assert "total_cost_usd" in keys


def test_alert_is_sent_once_then_suppressed_until_cooldown_expires(tmp_path: Path) -> None:
    report = _report()
    decision = evaluate_gate(report, CONFIG)
    state = tmp_path / "state.json"
    sender = Recorder()

    first = notify_gate_breach(
        report,
        decision,
        CONFIG,
        url="https://hooks.example/x",
        state_path=state,
        now=NOW,
        sender=sender,
    )
    second = notify_gate_breach(
        report,
        decision,
        CONFIG,
        url="https://hooks.example/x",
        state_path=state,
        now=NOW + timedelta(minutes=30),
        sender=sender,
    )
    third = notify_gate_breach(
        report,
        decision,
        CONFIG,
        url="https://hooks.example/x",
        state_path=state,
        now=NOW + timedelta(minutes=61),
        sender=sender,
    )

    assert first.sent and sorted(first.notified_keys) == ["pass_rate", "total_cost_usd"]
    assert not second.sent and sorted(second.suppressed_keys) == ["pass_rate", "total_cost_usd"]
    assert third.sent
    assert len(sender.calls) == 2
    assert set(json.loads(state.read_text())) == {"pass_rate", "total_cost_usd"}
    assert sender.calls[0][1]["event"] == "agenticlens.gate.failed"


def test_per_category_cooldown_lets_budget_alerts_repeat_sooner(tmp_path: Path) -> None:
    report = _report()
    decision = evaluate_gate(report, CONFIG)
    state = tmp_path / "state.json"
    sender = Recorder()
    options = {
        "url": "https://hooks.example/x",
        "state_path": state,
        "sender": sender,
        "cooldown": timedelta(hours=24),
        "cooldowns": {"budget": timedelta(minutes=10)},
    }

    notify_gate_breach(report, decision, CONFIG, now=NOW, **options)
    later = notify_gate_breach(report, decision, CONFIG, now=NOW + timedelta(minutes=15), **options)

    assert later.notified_keys == ["total_cost_usd"]
    assert later.suppressed_keys == ["pass_rate"]


@pytest.mark.parametrize(
    ("fmt", "key"), [("slack", "text"), ("teams", "@type"), ("generic", "breaches")]
)
def test_payload_formats(fmt: str, key: str) -> None:
    report = _report()
    decision = evaluate_gate(report, CONFIG)
    sender = Recorder()

    notify_gate_breach(
        report,
        decision,
        CONFIG,
        url="http://localhost:9/hook",
        webhook_format=fmt,  # type: ignore[arg-type]
        now=NOW,
        sender=sender,
    )

    payload = sender.calls[0][1]
    assert key in payload
    assert "nightly" in json.dumps(payload)


def test_passing_gate_sends_nothing() -> None:
    report = _report(pass_rate=1.0, cost=0.01)
    decision = evaluate_gate(report, CONFIG)
    sender = Recorder()

    result = notify_gate_breach(
        report, decision, CONFIG, url="https://hooks.example/x", now=NOW, sender=sender
    )

    assert decision.passed and not result.sent and sender.calls == []


@pytest.mark.parametrize("url", ["file:///etc/passwd", "hooks.example/x", "ftp://x/y"])
def test_non_http_urls_are_rejected(url: str) -> None:
    report = _report()
    with pytest.raises(ValueError, match="http"):
        notify_gate_breach(report, evaluate_gate(report, CONFIG), CONFIG, url=url, now=NOW)


def test_naive_now_is_rejected() -> None:
    report = _report()
    with pytest.raises(ValueError, match="timezone"):
        notify_gate_breach(
            report,
            evaluate_gate(report, CONFIG),
            CONFIG,
            url="https://hooks.example/x",
            now=datetime(2026, 1, 1),
            sender=Recorder(),
        )
