"""Build, review, approve, and run a regression suite from three sources.

Inputs (`examples/suites/inputs/`):

- `support_cases.csv`: hand-written cases, including PII and a duplicate row
- `traces/`: three production traces (one failed, so it is skipped)
- `feedback.json`: user feedback (a confirmation, a correction, and two
  records that cannot become cases)

The pipeline imports and converts them, masks PII, drops duplicates, adds
synthetic variations, assigns splits, records reviews, approves the suite into
an immutable store, exports it, and evaluates it. The agent is a deterministic
keyword stub so the demo stays offline and reproducible; replace
`support_agent` with your real agent.

    uv run python examples/suite_management_demo.py

writes `examples/suites/store/` and `examples/suites/artifacts/`. The same
steps run from the CLI; see `docs/suite-management.md`.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_evals import EvalTrace, EvaluationSample, TestSuite

from agenticlens.evaluation import GateConfig, default_registry, evaluate_gate, evaluate_suite
from agenticlens.models.trace import Run
from agenticlens.suites import (
    PIIMasker,
    SuiteStore,
    assign_splits,
    case_review_status,
    cases_from_feedback,
    cases_from_runs,
    drop_duplicates,
    find_duplicates,
    generate_variations,
    import_suite,
    load_feedback,
    mask_suite,
    merge_suites,
    remove_cases,
    review_cases,
    save_suite_file,
    summarize_suite,
)

EXAMPLE = Path(__file__).resolve().parent / "suites"
INPUTS = EXAMPLE / "inputs"
NAME, VERSION = "support-regression", "1.0.0"
#: Fixed so the stored version and every artifact are reproducible.
APPROVED_AT = datetime(2026, 10, 17, tzinfo=timezone.utc)

_ROUTES: tuple[tuple[tuple[str, ...], str, list[str]], ...] = (
    (
        ("refund", "return"),
        "Refunds are issued within 30 days to the original payment method.",
        ["lookup_policy"],
    ),
    (("password", "reset"), "We sent a reset link to your account email.", ["send_reset_link"]),
    (
        ("cancel",),
        "Your subscription is cancelled; you keep access until the period ends.",
        ["lookup_account", "cancel_subscription"],
    ),
    (("shipping", "parcel", "order"), "Your order ships in 2 business days.", ["lookup_order"]),
)


def support_agent(case_input: Any) -> tuple[str, list[str]]:
    """Deterministic stand-in for a support agent: (answer, tools called)."""
    text = json.dumps(case_input).lower()
    for keywords, answer, tools in _ROUTES:
        if any(keyword in text for keyword in keywords):
            return answer, tools
    return "Let me connect you with a specialist.", ["handoff"]


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_draft() -> tuple[TestSuite, dict[str, Any]]:
    """Import, convert, mask, de-duplicate, vary, split, and review."""
    imported = import_suite(INPUTS / "support_cases.csv", name=NAME, version=VERSION)
    runs = [
        Run.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted((INPUTS / "traces").glob("*.json"))
    ]
    from_traces = cases_from_runs(runs)
    from_feedback = cases_from_feedback(load_feedback(INPUTS / "feedback.json"), runs=runs)
    suite = merge_suites(
        imported,
        TestSuite(name=NAME, version=VERSION, cases=from_traces.cases),
        TestSuite(name=NAME, version=VERSION, cases=from_feedback.cases),
    )

    suite, masking = mask_suite(suite, PIIMasker())
    duplicates = find_duplicates(suite)
    suite = drop_duplicates(suite, duplicates)
    variants = generate_variations(suite, per_case=1, kinds=["prefix", "uppercase"], seed=7)
    suite = merge_suites(suite, TestSuite(name=NAME, version=VERSION, cases=variants))
    suite = assign_splits(suite, seed=7)

    # The reviewer rejects one synthetic variant and accepts everything else.
    rejected = "cancel-plan--prefix"
    suite = review_cases(
        suite,
        status="rejected",
        reviewer="support-qa",
        case_ids=[rejected],
        notes="Greeting-prefixed cancellations are routed to retention, not the bot.",
    )
    pending = [case.id for case in suite.cases if case_review_status(case) == "needs_review"]
    suite = review_cases(suite, status="accepted", reviewer="support-qa", case_ids=pending)
    suite = remove_cases(suite, [rejected])

    log = {
        "skipped_traces": [item.model_dump() for item in from_traces.skipped],
        "skipped_feedback": [item.model_dump() for item in from_feedback.skipped],
        "variants_added": len(variants),
        "rejected": [rejected],
    }
    return suite, {"masking": masking, "duplicates": duplicates, "log": log}


def run_agent(suite: TestSuite) -> list[EvaluationSample]:
    samples = []
    for case in suite.cases:
        answer, tools = support_agent(case.input)
        trace = EvalTrace(
            trace_id=f"replay-{case.id}",
            spans=[{"tool_name": tool} for tool in tools],
            total_latency_ms=300.0 * len(tools),
            estimated_cost_usd=0.00005 * len(tools),
            cost_source="estimated",
        )
        samples.append(EvaluationSample(case_id=case.id, output=answer, trace=trace))
    return samples


def main(out_dir: Path | None = None) -> dict[str, Any]:
    out = out_dir or EXAMPLE
    artifacts = out / "artifacts"
    draft, reports = build_draft()
    save_suite_file(draft, artifacts / "draft-suite.yaml")
    _write_json(artifacts / "masking-report.json", reports["masking"].model_dump(mode="json"))
    _write_json(artifacts / "duplicate-report.json", reports["duplicates"].model_dump(mode="json"))
    _write_json(artifacts / "build-log.json", reports["log"])

    store = SuiteStore(out / "store")
    record = store.approve(
        draft,
        approved_by="support-qa",
        approved_at=APPROVED_AT,
        notes="Initial regression suite from CSV, production traces, and feedback.",
    )
    approved = store.load_suite(NAME, VERSION)
    save_suite_file(approved, artifacts / "regression-suite.json")
    _write_json(artifacts / "summary.json", summarize_suite(approved).model_dump(mode="json"))

    samples = run_agent(approved)
    _write_json(
        artifacts / "samples.json",
        {"samples": [sample.model_dump(mode="json") for sample in samples]},
    )
    report = evaluate_suite(approved, samples, registry=default_registry())
    _write_json(artifacts / "evaluation.json", report.model_dump(mode="json"))
    decision = evaluate_gate(report, GateConfig(min_pass_rate=1.0, max_failed_cases=0))
    _write_json(artifacts / "gate.json", decision.model_dump(mode="json"))
    return {
        "version": f"{record.name}@{record.version}",
        "sha256": record.content_sha256,
        "cases": record.case_count,
        "passed": report.summary.passed_cases,
        "gate_passed": decision.passed,
    }


if __name__ == "__main__":
    result = main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    print(json.dumps(result, indent=2))
