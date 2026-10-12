"""Webhook alerts for release-gate breaches, with per-threshold cooldowns.

A scheduled or CI `gate` run that fails every hour should not page someone
every hour. Each breached threshold has a key (`pass_rate`, `total_cost_usd`,
`tag_pass_rate:safety`, ...); once an alert for a key is sent, further alerts
for that key on the same suite are suppressed until its cooldown expires. Cooldown state is a
small JSON file the caller owns, so it survives between CI runs when cached.

Payload shapes: `generic` (structured JSON), `slack` (incoming-webhook
`text`), and `teams` (MessageCard). Nothing is sent when the gate passes.
"""

import json
import urllib.request
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from agentic_evals import EvaluationReport, GateConfig, GateDecision
from pydantic import BaseModel, Field

WebhookFormat = Literal["generic", "slack", "teams"]
Sender = Callable[[str, dict[str, Any], float], None]


class Breach(BaseModel):
    key: str
    category: Literal["quality", "latency", "budget"]
    observed: float | int | None
    limit: float | int


class NotificationResult(BaseModel):
    sent: bool
    breaches: list[Breach] = Field(default_factory=list)
    notified_keys: list[str] = Field(default_factory=list)
    suppressed_keys: list[str] = Field(default_factory=list)
    payload: dict[str, Any] | None = None


def breached_thresholds(decision: GateDecision, config: GateConfig) -> list[Breach]:
    """Which configured thresholds the decision's observed values break.

    Computed from `config` and `decision.observed`, not by parsing reason
    text, so keys stay stable if the wording of gate reasons changes.
    """
    observed = decision.observed
    breaches: list[Breach] = []

    def check(
        key: str,
        category: Literal["quality", "latency", "budget"],
        limit: float | int | None,
        *,
        minimum: bool,
    ) -> None:
        if limit is None:
            return
        value = observed.get(key)
        broken = value is None or (value < limit if minimum else value > limit)
        if broken:
            breaches.append(Breach(key=key, category=category, observed=value, limit=limit))

    check("pass_rate", "quality", config.min_pass_rate, minimum=True)
    check("average_score", "quality", config.min_average_score, minimum=True)
    check("failed_cases", "quality", config.max_failed_cases, minimum=False)
    check("average_latency_ms", "latency", config.max_average_latency_ms, minimum=False)
    check("total_cost_usd", "budget", config.max_total_cost_usd, minimum=False)
    for tag, floor in config.min_tag_pass_rate.items():
        check(f"tag_pass_rate:{tag}", "quality", floor, minimum=True)
    for metric, floor in config.min_metric_pass_rate.items():
        check(f"metric_pass_rate:{metric}", "quality", floor, minimum=True)
    return breaches


def _load_state(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"notification state file {path} must hold a JSON object")
    return {str(key): str(value) for key, value in data.items()}


def _save_state(path: Path | None, state: Mapping[str, str]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(sorted(state.items())), indent=2), encoding="utf-8")


def describe_breach(breach: Breach) -> str:
    observed = "unavailable" if breach.observed is None else f"{breach.observed:g}"
    return f"{breach.key} is {observed} (limit {breach.limit:g})."


def state_key(report: EvaluationReport, breach_key: str) -> str:
    """Cooldown state key: per suite, so one suite's alert never silences another's."""
    return f"{report.suite_name}::{breach_key}"


def build_payload(
    report: EvaluationReport,
    decision: GateDecision,
    breaches: list[Breach],
    *,
    webhook_format: WebhookFormat,
) -> dict[str, Any]:
    title = f"AgenticLens release gate failed: {report.suite_name} {report.suite_version}"
    # Only the breaches being alerted on; suppressed ones stay quiet.
    reasons = [describe_breach(breach) for breach in breaches]
    lines = [f"• {reason}" for reason in reasons]
    if webhook_format == "slack":
        return {"text": "\n".join([f"*{title}*", *lines])}
    if webhook_format == "teams":
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title,
            "themeColor": "D13438",
            "title": title,
            "text": "<br>".join(lines),
        }
    return {
        "event": "agenticlens.gate.failed",
        "suite_name": report.suite_name,
        "suite_version": report.suite_version,
        "report_created_at": report.created_at.isoformat(),
        "reasons": reasons,
        "breaches": [breach.model_dump(mode="json") for breach in breaches],
        "observed": decision.observed,
    }


def _post_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        response.read()


def notify_gate_breach(
    report: EvaluationReport,
    decision: GateDecision,
    config: GateConfig,
    *,
    url: str,
    webhook_format: WebhookFormat = "generic",
    cooldown: timedelta = timedelta(hours=1),
    cooldowns: Mapping[str, timedelta] | None = None,
    state_path: Path | None = None,
    now: datetime | None = None,
    timeout_seconds: float = 10.0,
    sender: Sender | None = None,
) -> NotificationResult:
    """Send one webhook alert for the breached thresholds not in cooldown.

    `cooldowns` overrides `cooldown` per breach key or per category
    (`quality`, `latency`, `budget`); a key match wins over a category match.
    Only the keys actually alerted on have their cooldown restarted.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("webhook URL must be an absolute http(s) URL")
    if decision.passed:
        return NotificationResult(sent=False)
    breaches = breached_thresholds(decision, config)
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    overrides = dict(cooldowns or {})
    state = _load_state(state_path)

    due: list[Breach] = []
    suppressed: list[str] = []
    for breach in breaches:
        window = overrides.get(breach.key, overrides.get(breach.category, cooldown))
        last = state.get(state_key(report, breach.key))
        if last is not None and moment - datetime.fromisoformat(last) < window:
            suppressed.append(breach.key)
        else:
            due.append(breach)
    if not due:
        return NotificationResult(sent=False, breaches=breaches, suppressed_keys=suppressed)

    payload = build_payload(report, decision, due, webhook_format=webhook_format)
    (sender or _post_json)(url, payload, timeout_seconds)
    for breach in due:
        state[state_key(report, breach.key)] = moment.isoformat()
    _save_state(state_path, state)
    return NotificationResult(
        sent=True,
        breaches=breaches,
        notified_keys=[breach.key for breach in due],
        suppressed_keys=suppressed,
        payload=payload,
    )
