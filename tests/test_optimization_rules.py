"""Each optimization rule cites measured evidence and skips what it cannot measure."""

import pytest

from agenticlens.models.trace import RunStatus, SpanType
from agenticlens.optimization import (
    MemoryRule,
    OptimizationConfig,
    PromptCachingRule,
    PromptCompressionRule,
    RedundantStepRule,
    RetrievalRule,
    RetryPolicyRule,
    ToolCachingRule,
    UnnecessaryHandoffRule,
)
from agenticlens.optimization.rules import grade_confidence
from optimization_support import retrieval_run, run, span

CONFIG = OptimizationConfig()


def _prefix(digest: str = "abc", tokens: int = 1000, cached: int | None = None) -> dict:
    attrs = {"prompt.prefix_sha256": digest, "prompt.prefix_tokens": tokens}
    if cached is not None:
        attrs["prompt.cached_tokens"] = cached
    return attrs


def _model(run_id: str, index: int, **attrs) -> object:
    return span(run_id, index, SpanType.MODEL_CALL, tokens=(2000, 0), cost=0.02, attributes=attrs)


class TestPromptCaching:
    def test_repeats_after_the_first_are_priced_with_the_cache_discount(self):
        runs = [run(f"r{i}", [_model(f"r{i}", 1, **_prefix())]) for i in range(3)]
        [found] = PromptCachingRule().analyze(runs, CONFIG)
        assert found.kind == "prompt_caching"
        assert [e.run_id for e in found.evidence] == ["r1", "r2"]
        # Two repeats of 1000 tokens at 90% off, averaged over three runs.
        assert found.benefit.tokens_per_run == pytest.approx(2 * 1000 * 0.9 / 3)
        assert found.benefit.cost_usd_per_run == pytest.approx(2 * 0.02 * 0.5 * 0.9 / 3)
        assert found.runs_affected == 2 and found.runs_observed == 3

    def test_skips_prefixes_already_cached_or_too_short(self):
        cached = [run(f"r{i}", [_model(f"r{i}", 1, **_prefix(cached=1000))]) for i in range(3)]
        short = [run(f"s{i}", [_model(f"s{i}", 1, **_prefix(tokens=10))]) for i in range(3)]
        assert PromptCachingRule().analyze(cached + short, CONFIG) == []

    def test_unknown_span_cost_keeps_the_saving_unpriced(self):
        runs = [
            run("a", [_model("a", 1, **_prefix())]),
            run(
                "b",
                [
                    span(
                        "b",
                        1,
                        SpanType.MODEL_CALL,
                        tokens=(2000, 0),
                        cost=None,
                        attributes=_prefix(),
                    )
                ],
            ),
        ]
        [found] = PromptCachingRule().analyze(runs, CONFIG)
        assert found.benefit.cost_usd_per_run is None
        assert found.benefit.cost_available is False
        assert found.benefit.monthly_cost_usd is None


def test_prompt_compression_caps_confidence_at_medium():
    runs = [
        run(f"r{i}", [span(f"r{i}", 1, SpanType.MODEL_CALL, tokens=(8000, 100), cost=0.081)])
        for i in range(4)
    ]
    [found] = PromptCompressionRule().analyze(runs, CONFIG)
    assert found.confidence == "medium"
    assert found.benefit.tokens_per_run == pytest.approx(8000 * 0.3)
    assert found.risks[0].kind == "instruction_loss"
    balanced = [run("b", [span("b", 1, SpanType.MODEL_CALL, tokens=(8000, 1000))])]
    assert PromptCompressionRule().analyze(balanced, CONFIG) == []


class TestRetrieval:
    def test_top_k_never_cuts_a_chunk_any_answer_used(self):
        runs = [retrieval_run("a", [1, 2]), retrieval_run("b", [1, 3])]
        pruning = next(
            o for o in RetrievalRule().analyze(runs, CONFIG) if o.kind == "retrieval_pruning"
        )
        assert pruning.subject["recommended_top_k"] == 3
        # Five 100-token chunks cut per run, priced at the next model call.
        assert pruning.benefit.tokens_per_run == 500
        assert pruning.benefit.cost_usd_per_run == pytest.approx(500 * 0.01 / 1000)

    def test_deep_used_chunk_suggests_reranking_with_capped_confidence(self):
        runs = [retrieval_run("a", [6]), retrieval_run("b", [1])]
        found = {o.kind: o for o in RetrievalRule().analyze(runs, CONFIG)}
        rerank = found["retrieval_reranking"]
        assert rerank.runs_affected == 1
        assert rerank.evidence[0].measurements["unused_chunks_ranked_above"] == 5
        assert rerank.confidence == "low"

    def test_incomplete_chunk_usage_is_skipped(self):
        bad = run(
            "a",
            [
                span(
                    "a",
                    1,
                    SpanType.RETRIEVAL,
                    attributes={"chunks": [{"tokens": 10}] * 8},
                )
            ],
        )
        assert RetrievalRule().analyze([bad], CONFIG) == []

    def test_unpriced_downstream_call_leaves_cost_unavailable(self):
        runs = [retrieval_run("a", [1], cost=None)]
        [pruning] = RetrievalRule().analyze(runs, CONFIG)
        assert pruning.benefit.cost_usd_per_run is None


def test_memory_rule_flags_growth_and_budget_excess():
    reads = [
        span("a", i, SpanType.MEMORY_READ, tokens=(size, 0), cost=0.0)
        for i, size in enumerate((1000, 2000, 3000), start=1)
    ]
    runs = [run("a", [*reads, span("a", 9, SpanType.MODEL_CALL, tokens=(1000, 0), cost=0.07)])]
    [found] = MemoryRule().analyze(runs, CONFIG)
    assert found.evidence[0].measurements["grows_every_read"] is True
    assert "retention window" in found.action
    assert found.benefit.tokens_per_run == 6000 - CONFIG.memory_token_budget
    assert found.benefit.cost_usd_per_run == pytest.approx(4000 * 0.07 / 7000)
    small = [run("b", [span("b", 1, SpanType.MEMORY_READ, tokens=(100, 0))])]
    assert MemoryRule().analyze(small, CONFIG) == []


class TestToolCaching:
    def _calls(self, run_id: str, **attrs):
        return [
            span(
                run_id,
                i,
                SpanType.TOOL_CALL,
                tool_name="lookup",
                attributes={"tool_args": {"id": 1}, **attrs},
            )
            for i in (1, 2, 3)
        ]

    def test_repeats_with_identical_arguments_are_cacheable(self):
        [found] = ToolCachingRule().analyze([run("a", self._calls("a", idempotent=True))], CONFIG)
        assert found.subject == {"tool_name": "lookup"}
        assert found.benefit.tokens_per_run == 2 * 110
        assert found.benefit.latency_ms_per_run == 100
        assert found.risks[0].severity == "low"

    def test_undeclared_idempotency_is_a_medium_risk(self):
        [found] = ToolCachingRule().analyze([run("a", self._calls("a"))], CONFIG)
        assert found.risks[0].severity == "medium"

    def test_side_effects_and_failures_are_never_cached(self):
        side_effects = run("a", self._calls("a", side_effects=True))
        not_idempotent = run("b", self._calls("b", idempotent=False))
        failed = run(
            "c",
            [
                span(
                    "c",
                    i,
                    SpanType.TOOL_CALL,
                    status=RunStatus.FAILED,
                    tool_name="t",
                    attributes={"tool_args": {}},
                )
                for i in (1, 2)
            ],
        )
        assert ToolCachingRule().analyze([side_effects, not_idempotent, failed], CONFIG) == []


class TestRetryPolicy:
    def _run(self, run_id: str, *, recovers: bool):
        failure = span(
            run_id, 1, SpanType.TOOL_CALL, status=RunStatus.FAILED, error_type="auth_error"
        )
        retry = span(
            run_id,
            2,
            SpanType.RETRY,
            status=RunStatus.SUCCEEDED if recovers else RunStatus.FAILED,
            parent_span_id=failure.span_id,
        )
        return run(run_id, [failure, retry])

    def test_error_never_recovered_by_retry_is_non_retryable(self):
        [found] = RetryPolicyRule().analyze(
            [self._run("a", recovers=False), self._run("b", recovers=False)], CONFIG
        )
        assert found.subject == {"error_type": "auth_error"}
        assert found.benefit.tokens_per_run == 110

    def test_a_single_recovery_suppresses_the_recommendation(self):
        runs = [
            self._run("a", recovers=False),
            self._run("b", recovers=False),
            self._run("c", recovers=True),
        ]
        assert RetryPolicyRule().analyze(runs, CONFIG) == []


def test_redundant_step_requires_identical_input_and_output():
    def check(run_id: str, index: int, output: str):
        return span(
            run_id,
            index,
            SpanType.VALIDATION,
            name="check",
            input_data={"q": 1},
            output_data={"ok": output},
        )

    [found] = RedundantStepRule().analyze(
        [run("a", [check("a", 1, "y"), check("a", 2, "y")])], CONFIG
    )
    assert found.subject == {"span_type": "validation", "span_name": "check"}
    different = run("b", [check("b", 1, "y"), check("b", 2, "n")])
    assert RedundantStepRule().analyze([different], CONFIG) == []


class TestHandoff:
    def _handoff(self, run_id: str, child_type: SpanType, **fields):
        parent = span(
            run_id,
            1,
            SpanType.DELEGATION,
            attributes={"from_agent": "a", "to_agent": "b"},
            **fields,
        )
        child = span(run_id, 2, child_type, agent_name="b", parent_span_id=parent.span_id)
        return run(run_id, [parent, child])

    def test_receiver_without_work_is_unnecessary(self):
        [found] = UnnecessaryHandoffRule().analyze([self._handoff("r", SpanType.CUSTOM)], CONFIG)
        assert found.subject == {"from_agent": "a", "to_agent": "b"}
        assert found.evidence[0].span_ids == ["r-1", "r-2"]

    def test_receiver_that_works_is_kept_unless_it_echoes(self):
        working = self._handoff("w", SpanType.MODEL_CALL)
        assert UnnecessaryHandoffRule().analyze([working], CONFIG) == []
        echo = self._handoff("e", SpanType.MODEL_CALL, input_data="x", output_data="x")
        [found] = UnnecessaryHandoffRule().analyze([echo], CONFIG)
        assert found.evidence[0].measurements["output_equals_input"] is True


def test_confidence_grading():
    config = OptimizationConfig()
    assert grade_confidence(4, 4, True, config)[0] == "high"
    assert grade_confidence(2, 10, True, config)[0] == "medium"
    level, reasons = grade_confidence(1, 10, True, config)
    assert level == "low" and any("single run" in r for r in reasons)
    level, reasons = grade_confidence(4, 4, False, config)
    assert level == "medium" and any("incomplete" in r for r in reasons)
    assert grade_confidence(4, 4, True, config, cap="low")[0] == "low"


def test_opportunity_ids_are_stable_across_runs():
    runs = [retrieval_run("a", [1]), retrieval_run("b", [1])]
    first = [o.opportunity_id for o in RetrievalRule().analyze(runs, CONFIG)]
    second = [o.opportunity_id for o in RetrievalRule().analyze(list(reversed(runs)), CONFIG)]
    assert first == second


def test_one_unsafe_call_excludes_the_whole_tool():
    safe = [
        span("a", i, SpanType.TOOL_CALL, tool_name="lookup", attributes={"tool_args": {"id": 1}})
        for i in (1, 2)
    ]
    unsafe = span(
        "b",
        1,
        SpanType.TOOL_CALL,
        tool_name="lookup",
        attributes={"tool_args": {"id": 2}, "side_effects": True},
    )
    assert ToolCachingRule().analyze([run("a", safe), run("b", [unsafe])], CONFIG) == []
