"""Trace-aware evaluators and the span semantics the trace adapter carries."""

from typing import Any

import pytest

from agenticlens.evaluation import (
    EvalSpan,
    EvalTrace,
    EvaluationContext,
    EvaluationSample,
    EvaluatorConfig,
    default_registry,
    to_eval_trace,
    trace_evaluators,
)
from agenticlens.evaluation import (
    TestCase as EvalCase,
)
from agenticlens.evaluation._trace_adapter import to_eval_trace_dict
from agenticlens.evaluation.trace_evaluators import (
    TRACE_EVALUATORS,
    agent_goal,
    citation,
    completeness,
    groundedness,
    handoff,
    loop,
    relevance,
    safety,
    tool_trajectory,
)
from agenticlens.models.trace import Run
from diagnosis_support import run, span


def _context(
    *,
    output: str = "",
    trace: EvalTrace | Run | None = None,
    config: dict[str, Any] | None = None,
    case_input: Any = None,
    metadata: dict[str, Any] | None = None,
    expected_contains: list[str] | None = None,
) -> EvaluationContext:
    if isinstance(trace, Run):
        trace = to_eval_trace(trace)
    return EvaluationContext(
        case=EvalCase(
            id="c",
            name="c",
            input=case_input,
            max_turns=99,
            expected_contains=expected_contains or [],
            metadata=metadata or {},
        ),
        sample=EvaluationSample(case_id="c", output=output, trace=trace or EvalTrace()),
        config=EvaluatorConfig(name="x", config=config or {}),
    )


def _tools(*calls: tuple[str, dict[str, Any] | None]) -> Run:
    return run(
        [
            span(
                f"t{i}",
                name,
                "tool_call",
                i * 10,
                tool_name=name,
                agent_name="a",
                input_data=args,
                attributes={"tool_args": args} if args else {},
            )
            for i, (name, args) in enumerate(calls)
        ]
    )


def test_adapter_adds_namespaced_span_semantics_without_overwriting() -> None:
    trace = run(
        [
            span(
                "r",
                "kb",
                "retrieval",
                0,
                agent_name="a",
                output_data=["doc"],
                attributes={"agenticlens.name": "kept"},
            )
        ],
        task_success=True,
    )
    adapted = to_eval_trace(trace)
    attributes = adapted.spans[0].attributes
    assert attributes["agenticlens.span_type"] == "retrieval"
    assert attributes["agenticlens.agent_name"] == "a"
    assert attributes["agenticlens.status"] == "succeeded"
    assert attributes["agenticlens.retrieved"] == ["doc"]
    assert attributes["agenticlens.name"] == "kept"
    assert adapted.metadata["agenticlens.task_success"] is True
    as_dict = to_eval_trace_dict(trace.model_dump(mode="json"))
    assert as_dict["spans"][0]["attributes"]["agenticlens.span_type"] == "retrieval"
    assert as_dict["metadata"]["agenticlens.run_status"] == "succeeded"


@pytest.mark.parametrize(
    ("mode", "expected", "value"),
    [
        ("exact", ["search", "fetch"], 1.0),
        ("exact", ["fetch", "search"], 0.0),
        ("in_order", ["search", "answer", "fetch"], 2 / 3),
        ("any_order", ["fetch", "search", "fetch"], 2 / 3),
    ],
)
def test_tool_trajectory_modes(mode: str, expected: list[str], value: float) -> None:
    score = tool_trajectory(
        _context(
            trace=_tools(("search", None), ("fetch", None)),
            config={"expected": expected, "mode": mode},
        )
    )
    assert score.value == pytest.approx(value)


def test_tool_trajectory_skips_and_rejects_bad_mode() -> None:
    assert tool_trajectory(_context()).skipped
    with pytest.raises(ValueError):
        tool_trajectory(_context(config={"expected": ["a"], "mode": "fuzzy"}))


def test_agent_goal_checks() -> None:
    trace = run(
        [
            span("a", "plan", "model_call", 0, agent_name="planner"),
            span("w", "write", "final_response", 10, agent_name="writer"),
        ],
        task_success=True,
    )
    good = agent_goal(
        _context(
            output="Refund issued",
            trace=trace,
            config={"final_agent": "writer", "goal_contains": ["refund"]},
        )
    )
    assert good.passed and good.value == 1.0
    failed = run([span("t", "x", "tool_call", 0, status="failed")], failed=True, task_success=False)
    bad = agent_goal(_context(trace=failed))
    assert not bad.passed and bad.metadata["checks"]["task_success"] is False
    assert agent_goal(_context()).skipped


def test_handoff_limits() -> None:
    spans = []
    for i in range(3):
        spans += [
            span(f"go{i}", "h", "delegation", i * 40, agent_name="a", attributes={"to_agent": "b"}),
            span(
                f"back{i}",
                "h",
                "delegation",
                i * 40 + 20,
                agent_name="b",
                attributes={"to_agent": "a"},
            ),
        ]
    bouncing = handoff(_context(trace=run(spans)))
    assert not bouncing.passed and "bounced 3 times" in bouncing.explanation
    limited = handoff(
        _context(trace=run(spans[:1]), config={"allowed": ["a->c"], "max_handoffs": 0})
    )
    assert len(limited.metadata["problems"]) == 2
    assert handoff(_context(trace=run(spans[:1]))).passed
    assert handoff(_context()).skipped


def test_loop_detects_identical_streaks() -> None:
    same = _tools(*[("search", {"q": "x"})] * 4)
    score = loop(_context(trace=same))
    assert not score.passed and score.metadata["longest_streak"] == 4
    assert score.value == pytest.approx(0.5)
    varied = _tools(("search", {"q": 1}), ("search", {"q": 2}), ("search", {"q": 3}))
    assert loop(_context(trace=varied)).passed
    assert loop(_context()).explanation == "No tool calls recorded."


DOCS = [{"id": "kb-1", "text": "Refunds go to the original card within five business days."}]


def _rag(output_docs: Any = DOCS) -> Run:
    return run([span("r", "kb", "retrieval", 0, output_data=output_docs)])


def test_groundedness_uses_retrieved_documents() -> None:
    grounded = groundedness(
        _context(output="Refunds go to the original card within five days.", trace=_rag())
    )
    assert grounded.passed
    invented = groundedness(
        _context(output="Refunds arrive instantly as bonus vouchers today.", trace=_rag())
    )
    assert not invented.passed and invented.metadata["unsupported_sentences"]
    assert groundedness(_context(output="x")).skipped
    explicit = groundedness(
        _context(
            output="Paris is the capital of France.",
            config={"context": "Paris is the capital of France."},
        )
    )
    assert explicit.passed


def test_relevance_and_completeness() -> None:
    relevant = relevance(
        _context(
            output="Your refund arrives in five days.", case_input="When does my refund arrive?"
        )
    )
    assert relevant.value == 1.0
    assert relevance(_context(output="x")).skipped
    complete = completeness(
        _context(
            output="Refund to card in 5 days",
            config={"required_points": ["refund", ["5 days", "five"]]},
        )
    )
    assert complete.passed
    partial = completeness(_context(output="Refund soon", expected_contains=["refund", "card"]))
    assert partial.value == 0.5 and partial.metadata["missing_points"] == ["card"]
    assert completeness(_context(output="x")).skipped


def test_citations_must_match_retrieved_ids() -> None:
    assert citation(_context(output="See [kb-1].", trace=_rag())).passed
    wrong = citation(_context(output="See [kb-1] and [kb-9].", trace=_rag()))
    assert wrong.value == 0.5 and wrong.metadata["invalid"] == ["kb-9"]
    missing = citation(_context(output="No sources.", trace=_rag()))
    assert not missing.passed
    optional = citation(
        _context(output="No sources.", trace=_rag(), config={"require_citations": False})
    )
    assert optional.passed
    assert citation(_context(output="[a]", trace=_rag(["plain text"]))).skipped


def test_safety_checks_output_and_tool_arguments_without_echoing_values() -> None:
    leaky = _tools(("lookup", {"email": "jane@example.com"}))
    score = safety(_context(output="All good.", trace=leaky))
    assert not score.passed
    assert score.metadata["violations"] == ["email in tool_args:lookup#0"]
    assert "jane@example.com" not in score.explanation
    card = safety(_context(output="Card 4111 1111 1111 1111 on file"))
    assert "credit_card in output" in card.metadata["violations"]
    not_luhn = safety(_context(output="Order 1234 5678 9012 3456"))
    assert not_luhn.passed
    allowed = safety(_context(output="Mail help@shop.test", config={"allow": ["help@shop.test"]}))
    assert allowed.passed
    terms = safety(_context(output="internal only", config={"forbidden_terms": ["INTERNAL"]}))
    assert terms.metadata["violations"] == ["forbidden term in output"]
    ssn = safety(_context(output="SSN 123-45-6789, call 555-123-4567"))
    assert {"us_ssn in output", "phone in output"} <= set(ssn.metadata["violations"])


def test_registry_exposes_every_trace_evaluator_with_a_version() -> None:
    evaluators = trace_evaluators()
    assert [e.name for e in evaluators] == list(TRACE_EVALUATORS)
    assert all(e.version == "1.0" for e in evaluators)
    registry = default_registry()
    assert set(TRACE_EVALUATORS) <= set(registry.names())
    assert "exact_match" in registry.names()  # agentic-evals built-ins too


def test_evaluators_read_attributes_from_any_eval_trace_producer() -> None:
    trace = EvalTrace(
        spans=[
            EvalSpan(tool_name="search", attributes={"agenticlens.input_fingerprint": "f"}),
            EvalSpan(tool_name="search", attributes={"agenticlens.input_fingerprint": "f"}),
            EvalSpan(tool_name="search", attributes={"agenticlens.input_fingerprint": "f"}),
        ]
    )
    assert not loop(_context(trace=trace)).passed


def test_grouped_handoffs_are_not_bounces() -> None:
    spans = [
        span(f"h{i}", "h", "delegation", i * 10, agent_name=src, attributes={"to_agent": dst})
        for i, (src, dst) in enumerate([("a", "b"), ("a", "b"), ("b", "a"), ("b", "a")])
    ]
    assert handoff(_context(trace=run(spans))).passed


def test_tool_args_fingerprint_ignores_key_order() -> None:
    trace = run(
        [
            span(
                f"t{i}",
                "search",
                "tool_call",
                i * 10,
                tool_name="search",
                attributes={"tool_args": args},
            )
            for i, args in enumerate([{"a": 1, "b": 2}, {"b": 2, "a": 1}, {"a": 1, "b": 2}])
        ]
    )
    adapted = to_eval_trace(trace)
    fingerprints = {s.attributes["agenticlens.input_fingerprint"] for s in adapted.spans}
    assert len(fingerprints) == 1
    assert not loop(_context(trace=adapted)).passed
