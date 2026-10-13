"""Trace-aware evaluators, judge cost, and evaluator disagreement in one run.

Three recorded RAG support runs are scored with:

- trace-aware deterministic evaluators (tool trajectory, groundedness against
  what retrieval actually returned, citations, safety on output *and* tool
  arguments, loops), and
- a structured LLM judge that reports its own token usage and cost.

The judge here is a stub so the demo stays offline and reproducible; swap
`stub_judge` for a real model call. `analyze_scores()` then reports
deterministic and model-based results separately, totals judge cost apart
from the agent's own cost, and lists cases where the evaluators disagree.

    uv run python examples/advanced_evaluation_demo.py

writes `examples/advanced_evaluation/artifacts/` (report JSON, score
analysis, HTML). The deterministic half also runs from the CLI:

    agenticlens evaluate examples/advanced_evaluation/suite.yaml \\
        examples/advanced_evaluation/samples.json --score-analysis analysis.json
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agenticlens.evaluation import (
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    JudgeUsage,
    JudgeVerdict,
    analyze_scores,
    default_registry,
    evaluate_suite,
    load_suite,
    save_html_report,
    structured_judge,
    to_eval_trace,
)
from agenticlens.models.trace import Run, RunStatus, Span, SpanType

HERE = Path(__file__).resolve().parent / "advanced_evaluation"
T0 = datetime(2026, 10, 3, 10, 0, tzinfo=timezone.utc)

DOCS = [
    {"id": "kb-12", "text": "Refunds are issued to the original payment method within 5 days."},
    {"id": "kb-31", "text": "Orders shipped internationally cannot be refunded after 30 days."},
]

CASES: dict[str, dict[str, Any]] = {
    "grounded": {
        "output": "Refunds go to the original payment method within 5 days [kb-12].",
        "tools": [("kb_search", {"query": "refund timing"}), ("lookup_order", {"id": "A-1"})],
    },
    "ungrounded": {
        "output": "Refunds arrive instantly as store credit with a bonus voucher [kb-99].",
        "tools": [("kb_search", {"query": "refund timing"}), ("lookup_order", {"id": "A-2"})],
    },
    "leaky": {
        "output": "Refunds go to the original payment method within 5 days [kb-12].",
        "tools": [
            ("kb_search", {"query": "refund timing"}),
            ("lookup_order", {"email": "jane.doe@example.com"}),
        ],
    },
}

# What the stub judge "concludes" per case: it misses the citation problem in
# `ungrounded` (disagreeing with the deterministic checks) and has no view on
# the PII in tool arguments it never saw.
JUDGE_VERDICTS = {"grounded": "agree", "ungrounded": "agree", "leaky": "agree"}


def build_run(case_id: str, spec: dict[str, Any]) -> Run:
    spans: list[Span] = []
    clock = 0.0
    for index, (tool, arguments) in enumerate(spec["tools"]):
        start = T0 + timedelta(milliseconds=clock)
        is_search = tool == "kb_search"
        spans.append(
            Span(
                span_id=f"{case_id}-{index}",
                name=tool,
                span_type=SpanType.RETRIEVAL if is_search else SpanType.TOOL_CALL,
                agent_name="support",
                tool_name=tool,
                started_at=start,
                completed_at=start + timedelta(milliseconds=80),
                latency_ms=80,
                status=RunStatus.SUCCEEDED,
                output_data=DOCS if is_search else None,
                attributes={"tool_args": arguments},
                estimated_cost_usd=0.0,
            )
        )
        clock += 90
    answer_start = T0 + timedelta(milliseconds=clock)
    spans.append(
        Span(
            span_id=f"{case_id}-answer",
            name="answer",
            span_type=SpanType.FINAL_RESPONSE,
            agent_name="support",
            model_name="gpt-4o-mini",
            provider="openai",
            started_at=answer_start,
            completed_at=answer_start + timedelta(milliseconds=300),
            latency_ms=300,
            input_tokens=900,
            output_tokens=60,
            estimated_cost_usd=0.000171,
            status=RunStatus.SUCCEEDED,
        )
    )
    return Run(
        run_id=case_id,
        trace_id=f"trace-{case_id}",
        application_name="refund-rag",
        started_at=T0,
        completed_at=answer_start + timedelta(milliseconds=300),
        status=RunStatus.SUCCEEDED,
        task_success=True,
        spans=spans,
        metadata={"evaluated_model": "gpt-4o-mini"},
    )


def stub_judge(context: EvaluationContext) -> JudgeVerdict:
    """Stands in for a real model call; returns a verdict and its usage."""
    return JudgeVerdict(
        verdict=JUDGE_VERDICTS[context.case.id],  # type: ignore[arg-type]
        confidence=0.8,
        rationale="Answer addresses the refund question.",
        usage=JudgeUsage(
            cost_usd=0.0021, cost_source="measured", input_tokens=640, output_tokens=85
        ),
    )


def samples() -> list[EvaluationSample]:
    return [
        EvaluationSample(
            case_id=case_id, output=spec["output"], trace=to_eval_trace(build_run(case_id, spec))
        )
        for case_id, spec in CASES.items()
    ]


def main(out: Path = HERE / "artifacts") -> None:
    out.mkdir(parents=True, exist_ok=True)
    built = samples()
    (out.parent / "samples.json").write_text(
        json.dumps([s.model_dump(mode="json") for s in built], indent=2) + "\n", encoding="utf-8"
    )
    suite = load_suite(HERE / "suite.yaml")
    registry = default_registry()
    registry.register(
        structured_judge(
            "answer_quality",
            stub_judge,
            judge_model="claude-haiku-5-5",
            judge_provider="anthropic",
            version="1.0",
            prompt_version="answer-quality-v2",
            prompt_template="Does the answer resolve the customer's refund question? ...",
        )
    )
    # The judge runs on every case in addition to the suite's deterministic checks.
    for case in suite.cases:
        case.evaluators.append(EvaluatorConfig(name="answer_quality", threshold=0.5))
    report = evaluate_suite(suite, built, registry=registry)
    # Fixed timestamp keeps the saved artifacts reproducible.
    report.created_at = T0
    analysis = analyze_scores(report)

    (out / "evaluation.json").write_text(report.model_dump_json(indent=2) + "\n", "utf-8")
    (out / "score-analysis.json").write_text(analysis.model_dump_json(indent=2) + "\n", "utf-8")
    save_html_report(report, out / "evaluation.html")

    print(f"Cases passed: {report.summary.passed_cases}/{report.summary.total_cases}")
    det, model = analysis.deterministic, analysis.model_based
    print(f"Deterministic: {det.passed}/{det.total - det.skipped} passed")
    print(f"Model-based:   {model.passed}/{model.total - model.skipped} passed")
    print(
        f"Judge cost: ${analysis.judge_cost.total_cost_usd:.4f} "
        f"(agent cost ${analysis.agent_cost_usd or 0:.6f})"
    )
    for item in analysis.disagreements:
        print(f"Disagreement on {item.case_id}: passed by {item.passing}, failed by {item.failing}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "artifacts")
