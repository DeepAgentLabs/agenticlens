"""Find, decide on, and evaluate optimizations from recorded support-agent traces.

Reads the recorded traces in examples/optimization/traces (no model or
network calls), analyses them with examples/optimization/optimization.yaml,
records accept/reject/adopt decisions in a local ledger, and evaluates the
adopted tool-caching change against the traces recorded after adoption.

    python examples/optimization_demo.py

The CLI equivalent:

    agenticlens optimize analyze examples/optimization/traces/before \\
      --config examples/optimization/optimization.yaml --baseline-variant large \\
      --save examples/optimization/artifacts/report.json \\
      --markdown examples/optimization/artifacts/report.md
    agenticlens optimize decide examples/optimization/artifacts/report.json ID \\
      --status accepted --by platform-team --ledger ledger.jsonl
    agenticlens optimize outcome examples/optimization/artifacts/report.json ID \\
      --before examples/optimization/traces/before \\
      --after examples/optimization/traces/after --ledger ledger.jsonl
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agenticlens.optimization import (
    RecommendationDecision,
    RecommendationLedger,
    analyze_optimizations,
    evaluate_outcome,
    load_optimization_config,
    load_traces,
    render_optimization_markdown,
    render_outcome_markdown,
    report_sha256,
    save_optimization_report,
)

EXAMPLE = Path(__file__).resolve().parent / "optimization"
DECIDED_AT = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)


def main(output: Path | None = None) -> dict[str, Any]:
    output = output or EXAMPLE / "artifacts"
    output.mkdir(parents=True, exist_ok=True)
    before = load_traces([EXAMPLE / "traces/before"])
    after = load_traces([EXAMPLE / "traces/after"])
    report = analyze_optimizations(
        before,
        load_optimization_config(EXAMPLE / "optimization.yaml"),
        baseline_variant_id="large",
    )
    save_optimization_report(report, output / "report.json")

    by_kind = {item.kind: item.opportunity_id for item in report.opportunities}
    ledger_path = output / "ledger.jsonl"
    # Each run writes a fresh demo ledger. Real ledgers are append-only.
    if ledger_path.exists():
        ledger_path.unlink()
    ledger = RecommendationLedger(ledger_path)
    digest = report_sha256(report)
    for kind, status, reason, change in [
        ("tool_result_caching", "accepted", "lookup_order is read-only", None),
        ("tool_result_caching", "adopted", "memoized per run", "support-agent#412"),
        ("prompt_caching", "accepted", "prefix is static", None),
        ("unnecessary_handoff", "rejected", "billing handoff is an audit boundary", None),
    ]:
        ledger.record(
            report,
            RecommendationDecision(
                opportunity_id=by_kind[kind],
                report_sha256=digest,
                status=status,  # type: ignore[arg-type]
                decided_by="platform-team",
                decided_at=DECIDED_AT,
                reason=reason,
                change_reference=change,
            ),
        )
    statuses = ledger.summary(report)
    (output / "report.md").write_text(
        render_optimization_markdown(report, statuses), encoding="utf-8"
    )

    outcome = evaluate_outcome(report, by_kind["tool_result_caching"], before, after, ledger=ledger)
    (output / "outcome.json").write_text(outcome.model_dump_json(indent=2) + "\n", "utf-8")
    (output / "outcome.md").write_text(render_outcome_markdown(outcome), encoding="utf-8")

    result: dict[str, Any] = {
        "opportunities": sorted(by_kind),
        "statuses": {kind: statuses[by_kind[kind]] for kind in sorted(by_kind)},
        "baseline": report.tradeoffs.baseline_variant_id,
        "outcome": outcome.status,
        "realized_ratio": outcome.realized_ratio,
    }
    print(result)
    return result


if __name__ == "__main__":
    main()
