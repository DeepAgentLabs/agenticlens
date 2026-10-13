"""Build the controlled-failure corpus used to measure attribution accuracy.

Each scenario is a multi-agent support workflow with exactly one known root
cause, recorded as ground truth in the trace itself: injected faults carry
the agentic-chaos markers (`chaos.injected`), other cases set
`metadata["expected_faulty_span_id"]`. Variants change agents, latencies,
and add distractors -- a transient tool error that a retry recovers, extra
successful spans, and downstream failures caused by the root cause -- so the
attribution has to separate cause from consequence.

Output is deterministic (fixed seed and timestamps):

    uv run python examples/diagnosis/build_controlled_failures.py

writes `examples/diagnosis/controlled_failures/*.json`.
"""

import json
import random
import sys
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agenticlens.models.trace import Run, RunStatus, Span, SpanType

OUT = Path(__file__).resolve().parent / "controlled_failures"
T0 = datetime(2026, 10, 1, 9, 0, tzinfo=timezone.utc)
AGENT_SETS = [
    ("router", "billing", "writer"),
    ("triage", "refunds", "responder"),
    ("dispatcher", "account", "composer"),
    ("supervisor", "orders", "reporter"),
]


class Builder:
    """Accumulates spans on a clock so every scenario reads top to bottom."""

    def __init__(self, case_id: str, rng: random.Random) -> None:
        self.case_id = case_id
        self.rng = rng
        self.clock = 0.0
        self.spans: list[Span] = []
        self.counter = 0

    def span(
        self,
        name: str,
        span_type: SpanType,
        *,
        parent: str | None = None,
        agent: str | None = None,
        status: str = "succeeded",
        duration: float | None = None,
        **fields: Any,
    ) -> str:
        self.counter += 1
        span_id = f"{self.case_id}-s{self.counter:02d}"
        latency = duration if duration is not None else float(self.rng.randint(20, 120))
        start = T0 + timedelta(milliseconds=self.clock)
        self.clock += latency + 5
        tokens = fields.pop("tokens", (0, 0))
        self.spans.append(
            Span(
                span_id=span_id,
                parent_span_id=parent,
                name=name,
                span_type=span_type,
                agent_name=agent,
                started_at=start,
                completed_at=start + timedelta(milliseconds=latency),
                latency_ms=latency,
                input_tokens=tokens[0],
                output_tokens=tokens[1],
                status=RunStatus(status),
                **fields,
            )
        )
        return span_id

    def model(self, name: str, agent: str, parent: str | None = None, **fields: Any) -> str:
        tokens = (self.rng.randint(300, 900), self.rng.randint(40, 200))
        return self.span(
            name, SpanType.MODEL_CALL, parent=parent, agent=agent, tokens=tokens, **fields
        )

    def run(
        self, *, failed: bool, expected: str | None = None, task_success: bool | None = None
    ) -> Run:
        metadata: dict[str, Any] = {"scenario": self.case_id.rsplit("-", 1)[0]}
        if expected is not None:
            metadata["expected_faulty_span_id"] = expected
        return Run(
            run_id=self.case_id,
            trace_id=f"trace-{self.case_id}",
            application_name="support-desk",
            started_at=T0,
            completed_at=T0 + timedelta(milliseconds=self.clock),
            status=RunStatus.FAILED if failed else RunStatus.SUCCEEDED,
            task_success=(not failed) if task_success is None else task_success,
            spans=self.spans,
            metadata=metadata,
        )


def _distractor(b: Builder, agent: str, parent: str) -> None:
    """A transient tool error that a retry recovers: noise, not the cause."""
    failed = b.span(
        "crm_lookup",
        SpanType.TOOL_CALL,
        parent=parent,
        agent=agent,
        status="failed",
        tool_name="crm",
        error_type="ConnectionReset",
        error_message="connection reset by peer",
    )
    retry = b.span("retry crm_lookup", SpanType.RETRY, parent=failed, agent=agent, retry_number=1)
    b.span("crm_lookup", SpanType.TOOL_CALL, parent=retry, agent=agent, tool_name="crm")


def tool_timeout(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket", SpanType.DELEGATION, agent=router, attributes={"to_agent": worker}
    )
    b.model("plan", worker, parent=root)
    if noisy:
        _distractor(b, worker, root)
    tool = b.span(
        "fetch_invoice",
        SpanType.TOOL_CALL,
        parent=root,
        agent=worker,
        status="failed",
        tool_name="invoices",
        error_type="TimeoutError",
        error_message="invoice service timed out after 5s",
    )
    b.span(
        "retry fetch_invoice",
        SpanType.RETRY,
        parent=tool,
        agent=worker,
        status="failed",
        retry_number=1,
        error_type="TimeoutError",
    )
    b.span(
        "answer",
        SpanType.FINAL_RESPONSE,
        parent=root,
        agent=writer,
        status="failed",
        error_type="MissingData",
        error_message="no invoice to summarize",
    )
    return b.run(failed=True, expected=tool)


def recovered_then_validation(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket", SpanType.DELEGATION, agent=router, attributes={"to_agent": worker}
    )
    _distractor(b, worker, root)
    b.model("draft_reply", writer, parent=root)
    if noisy:
        b.span(
            "kb_search",
            SpanType.RETRIEVAL,
            parent=root,
            agent=worker,
            attributes={"result_count": 4},
        )
    check = b.span(
        "policy_check",
        SpanType.VALIDATION,
        parent=root,
        agent=writer,
        status="failed",
        error_type="PolicyViolation",
        error_message="reply promises a refund outside policy",
    )
    return b.run(failed=True, expected=check)


def injected_latency(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket", SpanType.DELEGATION, agent=router, attributes={"to_agent": worker}
    )
    b.model("plan", worker, parent=root)
    b.span(
        "kb_search",
        SpanType.RETRIEVAL,
        parent=root,
        agent=worker,
        duration=4200.0,
        attributes={
            "result_count": 3,
            "chaos.injected": True,
            "chaos.fault_type": "latency_spike",
            "chaos.event_id": f"evt-{b.case_id}",
        },
    )
    if noisy:
        b.model("summarize_docs", worker, parent=root)
    b.model(
        "draft_reply",
        writer,
        parent=root,
        status="failed",
        error_type="DeadlineExceeded",
        error_message="request deadline exceeded",
    )
    return b.run(failed=True)


def injected_tool_error(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket", SpanType.DELEGATION, agent=router, attributes={"to_agent": worker}
    )
    if noisy:
        _distractor(b, worker, root)
    b.span(
        "update_order",
        SpanType.TOOL_CALL,
        parent=root,
        agent=worker,
        status="failed",
        tool_name="orders",
        error_type="HTTP503",
        error_message="service unavailable",
        attributes={
            "chaos.injected": True,
            "chaos.fault_type": "http_503",
            "chaos.event_id": f"evt-{b.case_id}",
        },
    )
    b.model("draft_reply", writer, parent=root)
    return b.run(failed=False, task_success=False)


def tool_loop(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket", SpanType.DELEGATION, agent=router, attributes={"to_agent": worker}
    )
    b.model("plan", worker, parent=root)
    first = None
    for _ in range(4):
        b.model("decide_next", worker, parent=root)
        call = b.span(
            "search_orders",
            SpanType.TOOL_CALL,
            parent=root,
            agent=worker,
            tool_name="order_search",
            input_data={"query": "order 1182"},
        )
        first = first or call
    if noisy:
        b.span(
            "kb_search",
            SpanType.RETRIEVAL,
            parent=root,
            agent=worker,
            attributes={"result_count": 2},
        )
    b.model("answer", writer, parent=root)
    return b.run(failed=False, expected=first, task_success=False)


def planner_model_error(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket",
        SpanType.DELEGATION,
        agent=router,
        status="failed",
        attributes={"to_agent": worker},
        error_type="AgentFailed",
    )
    if noisy:
        _distractor(b, worker, root)
    plan = b.model(
        "plan",
        worker,
        parent=root,
        status="failed",
        error_type="RateLimitError",
        error_message="429 Too Many Requests",
    )
    b.span(
        "answer",
        SpanType.FINAL_RESPONSE,
        parent=root,
        agent=writer,
        status="failed",
        error_type="NoPlan",
    )
    return b.run(failed=True, expected=plan)


def empty_retrieval(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket", SpanType.DELEGATION, agent=router, attributes={"to_agent": worker}
    )
    b.model("plan", worker, parent=root)
    if noisy:
        _distractor(b, worker, root)
    search = b.span(
        "kb_search", SpanType.RETRIEVAL, parent=root, agent=worker, attributes={"result_count": 0}
    )
    b.model("answer", writer, parent=root)
    return b.run(failed=False, expected=search, task_success=False)


def stagnation(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket", SpanType.DELEGATION, agent=router, attributes={"to_agent": worker}
    )
    first = None
    for _ in range(3):
        call = b.model("plan", worker, parent=root, output_data={"next": "ask_clarification"})
        first = first or call
    if noisy:
        b.span(
            "kb_search",
            SpanType.RETRIEVAL,
            parent=root,
            agent=worker,
            attributes={"result_count": 3},
        )
    b.model("answer", writer, parent=root)
    return b.run(failed=False, expected=first, task_success=False)


def handoff_loop(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    first = None
    for _ in range(3):
        go = b.span(
            f"handoff to {worker}",
            SpanType.DELEGATION,
            agent=router,
            attributes={"to_agent": worker},
        )
        b.model("assess", worker, parent=go)
        first = first or go
        back = b.span(
            f"handoff to {router}",
            SpanType.DELEGATION,
            agent=worker,
            attributes={"to_agent": router},
        )
        b.model("reroute", router, parent=back)
    if noisy:
        b.model("summarize", writer)
    return b.run(failed=False, expected=first, task_success=False)


def nested_tool_failure(b: Builder, agents: tuple[str, str, str], noisy: bool) -> Run:
    router, worker, writer = agents
    root = b.span(
        "handle_ticket",
        SpanType.DELEGATION,
        agent=router,
        status="failed",
        attributes={"to_agent": worker},
        error_type="DelegationFailed",
    )
    sub = b.span(
        "refund_workflow",
        SpanType.CUSTOM,
        parent=root,
        agent=worker,
        status="failed",
        error_type="StepFailed",
    )
    if noisy:
        b.model("plan", worker, parent=sub)
    tool = b.span(
        "issue_refund",
        SpanType.TOOL_CALL,
        parent=sub,
        agent=worker,
        status="failed",
        tool_name="payments",
        error_type="CardDeclined",
        error_message="payment processor declined the refund",
    )
    b.span("answer", SpanType.FINAL_RESPONSE, parent=root, agent=writer)
    return b.run(failed=True, expected=tool)


SCENARIOS: dict[str, Callable[[Builder, tuple[str, str, str], bool], Run]] = {
    "tool-timeout": tool_timeout,
    "recovered-then-validation": recovered_then_validation,
    "injected-latency": injected_latency,
    "injected-tool-error": injected_tool_error,
    "tool-loop": tool_loop,
    "planner-model-error": planner_model_error,
    "empty-retrieval": empty_retrieval,
    "stagnation": stagnation,
    "handoff-loop": handoff_loop,
    "nested-tool-failure": nested_tool_failure,
}


EXPECTED_CATEGORIES = {
    "tool-timeout": "timeout",
    "recovered-then-validation": "validation_failure",
    "injected-latency": "injected_fault",
    "injected-tool-error": "injected_fault",
    "tool-loop": "tool_loop",
    "planner-model-error": "model_error",
    "empty-retrieval": "empty_retrieval",
    "stagnation": "stagnation",
    "handoff-loop": "handoff_loop",
    "nested-tool-failure": "tool_error",
}


def build(out: Path = OUT) -> list[Path]:
    rng = random.Random(20261013)
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.json"):
        stale.unlink()
    written: list[Path] = []
    for name, scenario in SCENARIOS.items():
        for index, agents in enumerate(AGENT_SETS):
            case_id = f"{name}-{index + 1}"
            run = scenario(Builder(case_id, rng), agents, noisy=index % 2 == 1)
            run.metadata["expected_category"] = EXPECTED_CATEGORIES[name]
            path = out / f"{case_id}.json"
            path.write_text(
                json.dumps(run.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8"
            )
            written.append(path)
    return written


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    print(f"Wrote {len(build(target))} controlled failures to {target}")
