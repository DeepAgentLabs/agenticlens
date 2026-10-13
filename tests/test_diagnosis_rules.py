"""Deterministic diagnosis rules and the failure taxonomy."""

import pytest

from agenticlens.diagnosis import (
    FAILURE_TAXONOMY,
    DiagnosisConfig,
    FailureCategory,
    describe,
    diagnose_run,
)
from agenticlens.diagnosis.taxonomy import max_severity
from diagnosis_support import run, span


def _categories(report_run: object) -> list[str]:
    report = diagnose_run(report_run)  # type: ignore[arg-type]
    return [d.category.value for d in report.diagnoses]


def test_every_category_has_a_taxonomy_entry() -> None:
    assert set(FAILURE_TAXONOMY) == set(FailureCategory)
    for category in FailureCategory:
        info = describe(category)
        assert 0 < info.attribution_weight <= 1
        assert info.description and info.next_step


def test_max_severity_orders_levels() -> None:
    assert max_severity(["low", "high", "medium"]) == "high"
    assert max_severity([]) == "low"


def test_failed_tool_span_is_diagnosed_with_evidence() -> None:
    trace = run(
        [
            span(
                "t",
                "search",
                "tool_call",
                0,
                status="failed",
                tool_name="web",
                error_type="HTTP500",
                error_message="boom.",
            )
        ],
        failed=True,
    )
    report = diagnose_run(trace)
    [diagnosis] = report.diagnoses
    assert diagnosis.category is FailureCategory.TOOL_ERROR
    assert diagnosis.origin_span_id == "t"
    assert diagnosis.summary.endswith("boom.")
    assert diagnosis.evidence[0].span_id == "t"
    assert diagnosis.evidence[0].details["error_type"] == "HTTP500"
    assert diagnosis.rule_id == "failed_span" and diagnosis.rule_version == "1.0"


@pytest.mark.parametrize(
    ("span_type", "category"),
    [
        ("model_call", "model_error"),
        ("planning", "model_error"),
        ("retrieval", "retrieval_error"),
        ("validation", "validation_failure"),
        ("delegation", "delegation_failure"),
        ("memory_read", "tool_error"),
    ],
)
def test_failed_span_category_follows_span_type(span_type: str, category: str) -> None:
    assert _categories(run([span("a", "x", span_type, 0, status="failed")], failed=True)) == [
        category
    ]


def test_timeouts_are_detected_from_error_text_and_timeout_attribute() -> None:
    by_text = run([span("a", "x", "tool_call", 0, status="failed", error_type="TimeoutError")])
    by_limit = run(
        [span("a", "x", "tool_call", 0, 500, status="failed", attributes={"timeout_ms": 500})]
    )
    assert _categories(by_text) == ["timeout"]
    assert _categories(by_limit) == ["timeout"]


def test_failure_propagation_starts_at_the_deepest_failed_span() -> None:
    trace = run(
        [
            span("root", "agent", "delegation", 0, 100, status="failed"),
            span("child", "lookup", "tool_call", 10, status="failed", parent_span_id="root"),
        ],
        failed=True,
    )
    [diagnosis] = diagnose_run(trace).diagnoses
    assert diagnosis.origin_span_id == "child"
    assert diagnosis.span_ids == ["child", "root"]
    assert "propagated to 'agent'" in diagnosis.summary


def test_failed_retry_children_do_not_hide_the_original_failure() -> None:
    trace = run(
        [
            span("t", "fetch", "tool_call", 0, status="failed", error_type="Timeout"),
            span(
                "r", "retry fetch", "retry", 20, status="failed", parent_span_id="t", retry_number=1
            ),
        ],
        failed=True,
    )
    report = diagnose_run(trace)
    assert {d.category.value for d in report.diagnoses} == {"timeout", "retry_exhausted"}
    assert all(d.origin_span_id == "t" for d in report.diagnoses)


def test_identical_failures_merge_into_one_diagnosis() -> None:
    trace = run(
        [
            span("a", "fetch", "tool_call", 0, status="failed", tool_name="api", error_type="E"),
            span("b", "fetch", "tool_call", 20, status="failed", tool_name="api", error_type="E"),
        ],
        failed=True,
    )
    [diagnosis] = diagnose_run(trace).diagnoses
    assert diagnosis.span_ids == ["a", "b"]
    assert "2 occurrences" in diagnosis.summary


def test_recovered_failure_is_marked_low_severity() -> None:
    trace = run(
        [
            span("a", "fetch", "tool_call", 0, status="failed", tool_name="api"),
            span("r", "retry", "retry", 20, parent_span_id="a", retry_number=1),
        ]
    )
    [diagnosis] = diagnose_run(trace).diagnoses
    assert diagnosis.recovered is True
    assert diagnosis.severity == "low"
    assert diagnosis.evidence[-1].source == "trace.recovery"


def test_later_success_of_the_same_operation_counts_as_recovery() -> None:
    trace = run(
        [
            span("a", "fetch", "tool_call", 0, status="failed", tool_name="api"),
            span("b", "fetch", "tool_call", 20, tool_name="api"),
        ]
    )
    assert diagnose_run(trace).diagnoses[0].recovered is True


def test_successful_retry_is_not_exhausted() -> None:
    trace = run(
        [
            span("a", "fetch", "tool_call", 0, status="failed"),
            span("r", "retry", "retry", 20, status="failed", parent_span_id="a"),
            span("c", "fetch", "tool_call", 25, parent_span_id="r"),
        ]
    )
    assert "retry_exhausted" not in _categories(trace)


def test_tool_loop_uses_input_fingerprints() -> None:
    calls = [
        span(
            f"c{i}",
            "search",
            "tool_call",
            i * 20,
            tool_name="search",
            input_data={"q": "same"},
            agent_name="a",
        )
        for i in range(3)
    ]
    report = diagnose_run(run(calls))
    [loop] = report.diagnoses
    assert loop.category is FailureCategory.TOOL_LOOP
    assert loop.span_ids == ["c0", "c1", "c2"]
    assert loop.confidence == 0.9


def test_tool_loop_breaks_on_different_inputs_and_respects_threshold() -> None:
    calls = [
        span(f"c{i}", "search", "tool_call", i * 20, tool_name="search", input_data={"q": i})
        for i in range(4)
    ]
    assert _categories(run(calls)) == []
    same = [span(f"s{i}", "search", "tool_call", i * 20, tool_name="search") for i in range(3)]
    report = diagnose_run(run(same), config=DiagnosisConfig(loop_threshold=4))
    assert report.diagnoses == []
    lowered = diagnose_run(run(same)).diagnoses[0]
    assert lowered.confidence == 0.6  # no captured input to compare


def test_handoff_loop_requires_round_trips() -> None:
    spans = []
    for i in range(2):
        spans.append(
            span(
                f"go{i}", "to b", "delegation", i * 40, agent_name="a", attributes={"to_agent": "b"}
            )
        )
        spans.append(
            span(
                f"back{i}",
                "to a",
                "delegation",
                i * 40 + 20,
                agent_name="b",
                attributes={"to_agent": "a"},
            )
        )
    [loop] = diagnose_run(run(spans)).diagnoses
    assert loop.category is FailureCategory.HANDOFF_LOOP
    assert loop.origin_span_id == "go0"
    once = diagnose_run(run(spans[:2]))
    assert once.diagnoses == []


def test_handoff_target_falls_back_to_child_agent() -> None:
    spans = []
    for i in range(2):
        spans += [
            span(f"go{i}", "handoff", "delegation", i * 80, agent_name="a"),
            span(
                f"w{i}", "work", "model_call", i * 80 + 5, parent_span_id=f"go{i}", agent_name="b"
            ),
            span(f"back{i}", "handoff", "delegation", i * 80 + 40, agent_name="b"),
            span(
                f"v{i}",
                "work",
                "model_call",
                i * 80 + 45,
                parent_span_id=f"back{i}",
                agent_name="a",
            ),
        ]
    assert _categories(run(spans)) == ["handoff_loop"]


def test_stagnation_needs_identical_captured_outputs() -> None:
    same = [
        span(f"m{i}", "plan", "model_call", i * 20, agent_name="p", output_data={"next": "x"})
        for i in range(3)
    ]
    assert _categories(run(same)) == ["stagnation"]
    uncaptured = [span(f"u{i}", "plan", "model_call", i * 20) for i in range(3)]
    assert _categories(run(uncaptured)) == []


@pytest.mark.parametrize(
    "fields",
    [
        {"attributes": {"result_count": 0}},
        {"attributes": {"documents": []}},
        {"output_data": []},
    ],
)
def test_empty_retrieval(fields: dict[str, object]) -> None:
    assert _categories(run([span("r", "kb", "retrieval", 0, **fields)])) == ["empty_retrieval"]


def test_retrieval_with_results_or_unknown_count_is_not_empty() -> None:
    assert _categories(run([span("r", "kb", "retrieval", 0, attributes={"result_count": 2})])) == []
    assert _categories(run([span("r", "kb", "retrieval", 0)])) == []


def test_budget_rule_cites_top_contributors() -> None:
    spans = [
        span("a", "big", "model_call", 0, input_tokens=900, estimated_cost_usd=0.9),
        span("b", "small", "model_call", 20, input_tokens=100, estimated_cost_usd=0.1),
    ]
    report = diagnose_run(
        run(spans), config=DiagnosisConfig(max_cost_usd=0.5, max_total_tokens=500)
    )
    budgets = [d for d in report.diagnoses if d.category is FailureCategory.BUDGET_EXCEEDED]
    assert len(budgets) == 2
    assert all(d.origin_span_id == "a" for d in budgets)
    assert budgets[0].evidence[0].details["budget"] in (0.5, 500.0)


def test_cost_budget_with_unknown_cost_is_a_limitation() -> None:
    report = diagnose_run(
        run([span("a", "x", "model_call", 0)]), config=DiagnosisConfig(max_cost_usd=0.1)
    )
    assert report.diagnoses == []
    assert any("Cost budget not checked" in item for item in report.limitations)


def test_incomplete_task_fallback_only_when_nothing_else_explains_failure() -> None:
    trace = run(
        [span("a", "plan", "model_call", 0), span("f", "answer", "final_response", 20)],
        task_success=False,
    )
    [fallback] = diagnose_run(trace).diagnoses
    assert fallback.category is FailureCategory.INCOMPLETE_TASK
    assert fallback.origin_span_id == "f"
    assert fallback.confidence == 0.4

    explained = run([span("t", "x", "tool_call", 0, status="failed")], failed=True)
    assert "incomplete_task" not in _categories(explained)


def test_injected_fault_on_failed_span() -> None:
    trace = run(
        [
            span(
                "t",
                "x",
                "tool_call",
                0,
                status="failed",
                attributes={"chaos.injected": True, "chaos.fault_type": "http_503"},
            )
        ],
        failed=True,
    )
    [diagnosis] = diagnose_run(trace).diagnoses
    assert diagnosis.category is FailureCategory.INJECTED_FAULT
    assert diagnosis.confidence == 1.0
    assert "http_503" in diagnosis.summary


def test_injected_fault_on_successful_span_is_absorbed_only_if_run_succeeds() -> None:
    injected = span("k", "kb", "retrieval", 0, attributes={"chaos.fault_type": "latency"})
    absorbed = diagnose_run(run([injected])).diagnoses[0]
    assert absorbed.category is FailureCategory.INJECTED_FAULT and absorbed.recovered
    failed = diagnose_run(run([injected], task_success=False)).diagnoses[0]
    assert not failed.recovered


def test_custom_rule_set_replaces_defaults() -> None:
    from agenticlens.diagnosis.rules import EmptyRetrievalRule

    trace = run(
        [
            span("t", "x", "tool_call", 0, status="failed"),
            span("r", "kb", "retrieval", 20, attributes={"result_count": 0}),
        ]
    )
    report = diagnose_run(trace, rules=[EmptyRetrievalRule()])
    assert [d.category.value for d in report.diagnoses] == ["empty_retrieval"]
    assert [r.rule_id for r in report.rules] == ["empty_retrieval", "incomplete_task"]
