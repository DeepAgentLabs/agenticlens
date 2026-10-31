"""Write the recorded support-agent traces used by the optimization example.

Deterministic: fixed IDs, timestamps, token counts and costs. No model or
network calls. `before/` holds two variants (a large and a small answer
model) of the same workflow; `after/` is the same workload once tool-result
caching was adopted, so its outcome can be evaluated.

    python examples/optimization/record_traces.py
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agenticlens.models.trace import Run, RunStatus, Span, SpanType

HERE = Path(__file__).resolve().parent
START = datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc)
PREFIX = "a1f3c9" * 10 + "d2e4"  # sha256-shaped stand-in for the shared system prompt
#: Used chunk ranks per run index; run 2 needs a deep chunk, which also suggests reranking.
USED_RANKS = [[1, 2], [1, 3], [1, 5], [2]]
PRICE = {"large": 0.000004, "small": 0.0000015}


class _Builder:
    def __init__(self, run_id: str, offset: int, price: float) -> None:
        self.run_id = run_id
        self.clock = START + timedelta(hours=offset)
        self.price = price
        self.spans: list[Span] = []

    def add(
        self,
        name: str,
        span_type: SpanType,
        *,
        tokens: tuple[int, int] = (0, 0),
        latency_ms: float = 100.0,
        status: RunStatus = RunStatus.SUCCEEDED,
        price: float | None = None,
        **fields: Any,
    ) -> Span:
        started = self.clock
        self.clock += timedelta(milliseconds=latency_ms)
        span = Span(
            span_id=f"{self.run_id}-{len(self.spans) + 1:02d}",
            name=name,
            span_type=span_type,
            started_at=started,
            completed_at=self.clock,
            latency_ms=latency_ms,
            input_tokens=tokens[0],
            output_tokens=tokens[1],
            estimated_cost_usd=round(sum(tokens) * (self.price if price is None else price), 9),
            status=status,
            **fields,
        )
        self.spans.append(span)
        return span


def build_run(variant: str, index: int, *, cached_tools: bool) -> Run:
    phase = "after" if cached_tools else "before"
    run_id = f"{phase}-{variant}-{index + 1}"
    offset = index + (100 if cached_tools else 0) + (10 if variant == "small" else 0)
    b = _Builder(run_id, offset, PRICE[variant])
    prefix = {"prompt.prefix_sha256": PREFIX, "prompt.prefix_tokens": 1200}
    b.add(
        "plan",
        SpanType.MODEL_CALL,
        tokens=(1500, 200),
        latency_ms=900,
        model_name=f"support-{variant}",
        agent_name="triage",
        attributes=prefix,
    )
    used = USED_RANKS[index % len(USED_RANKS)]
    chunks = [
        {"rank": rank, "tokens": 150, "used": rank in used, "id": f"kb-{rank}"}
        for rank in range(1, 9)
    ]
    b.add(
        "kb_search",
        SpanType.RETRIEVAL,
        tokens=(20, 0),
        latency_ms=180,
        price=0.0000001,
        attributes={"retrieval.chunks": chunks},
    )
    for turn, size in enumerate((1500, 2200, 3000), start=1):
        b.add(
            f"memory_turn_{turn}", SpanType.MEMORY_READ, tokens=(size, 0), latency_ms=30, price=0.0
        )
    lookup = {"tool_args": {"order_id": f"A-{index + 1}"}, "idempotent": True}
    calls = 1 if cached_tools else 2
    for _ in range(calls):
        b.add(
            "lookup_order",
            SpanType.TOOL_CALL,
            tokens=(200, 100),
            latency_ms=400,
            tool_name="lookup_order",
            attributes=lookup,
        )
    refund = b.add(
        "refund_api",
        SpanType.TOOL_CALL,
        tokens=(150, 30),
        latency_ms=250,
        tool_name="refund_api",
        status=RunStatus.FAILED,
        error_type="auth_error",
    )
    for attempt in (1, 2):
        b.add(
            "refund_api_retry",
            SpanType.RETRY,
            tokens=(150, 30),
            latency_ms=250,
            status=RunStatus.FAILED,
            error_type="auth_error",
            retry_number=attempt,
            parent_span_id=refund.span_id,
        )
    handoff = b.add(
        "handoff_billing",
        SpanType.DELEGATION,
        tokens=(400, 20),
        latency_ms=120,
        agent_name="triage",
        attributes={"from_agent": "triage", "to_agent": "billing"},
    )
    b.add(
        "billing_ack",
        SpanType.CUSTOM,
        tokens=(0, 0),
        latency_ms=20,
        agent_name="billing",
        parent_span_id=handoff.span_id,
    )
    for _ in range(2):
        b.add(
            "policy_check",
            SpanType.VALIDATION,
            tokens=(300, 10),
            latency_ms=60,
            input_data={"draft": f"refund-{index}"},
            output_data={"allowed": True},
        )
    b.add(
        "answer",
        SpanType.MODEL_CALL,
        tokens=(5200, 150),
        latency_ms=1600,
        model_name=f"support-{variant}",
        agent_name="triage",
        attributes=prefix,
    )
    b.add("reply", SpanType.FINAL_RESPONSE, latency_ms=10, price=0.0)
    return Run(
        run_id=run_id,
        trace_id=f"trace-{run_id}",
        application_name="support-agent",
        task_type="refund_request",
        experiment_id="support-optimization",
        variant_id=variant,
        started_at=START + timedelta(hours=offset),
        completed_at=b.clock,
        status=RunStatus.SUCCEEDED,
        spans=b.spans,
        # The small model misses one refund out of four.
        task_success=not (variant == "small" and index == 3),
    )


def main() -> None:
    for phase, cached in (("before", False), ("after", True)):
        folder = HERE / "traces" / phase
        folder.mkdir(parents=True, exist_ok=True)
        for variant in ("large", "small"):
            for index in range(4):
                run = build_run(variant, index, cached_tools=cached)
                (folder / f"{run.run_id}.json").write_text(
                    run.model_dump_json(indent=2) + "\n", encoding="utf-8"
                )


if __name__ == "__main__":
    main()
