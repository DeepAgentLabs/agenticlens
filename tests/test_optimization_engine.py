"""The optimization report is ranked, reproducible, and validates its inputs."""

import pytest

from agenticlens.models.trace import SpanType
from agenticlens.optimization import (
    OptimizationConfig,
    analyze_optimizations,
    load_optimization_config,
    load_optimization_report,
    load_traces,
    render_optimization_markdown,
    save_optimization_report,
)
from optimization_support import retrieval_run, run, span


def test_ranking_puts_priced_opportunities_first():
    priced = retrieval_run("a", [1])
    unpriced = run(
        "b",
        [
            span("b", i, SpanType.TOOL_CALL, cost=None, tool_name="t", attributes={"tool_args": {}})
            for i in (1, 2, 3, 4)
        ],
    )
    report = analyze_optimizations([priced, unpriced])
    costs = [o.benefit.cost_usd_per_run for o in report.opportunities]
    assert costs[0] is not None and costs[-1] is None
    assert report.total_cost_usd is None


def test_report_is_reproducible_and_round_trips(tmp_path):
    runs = [retrieval_run("a", [1]), retrieval_run("b", [6])]
    first = analyze_optimizations(runs)
    assert first == analyze_optimizations(runs)
    save_optimization_report(first, tmp_path / "report.json")
    assert load_optimization_report(tmp_path / "report.json") == first
    assert "Lower top-k for 'kb'" in render_optimization_markdown(first)


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError, match="at least one"):
        analyze_optimizations([])
    duplicate = retrieval_run("a", [1])
    with pytest.raises(ValueError, match="unique"):
        analyze_optimizations([duplicate, duplicate])


def test_custom_rules_and_monthly_projection():
    report = analyze_optimizations(
        [retrieval_run("a", [1])], OptimizationConfig(monthly_runs=1000), rules=[]
    )
    assert report.opportunities == []
    [found] = [
        o
        for o in analyze_optimizations(
            [retrieval_run("a", [1])], OptimizationConfig(monthly_runs=1000)
        ).opportunities
        if o.kind == "retrieval_pruning"
    ]
    assert found.benefit.monthly_cost_usd == pytest.approx(found.benefit.cost_usd_per_run * 1000)


def test_config_and_trace_loading(tmp_path):
    (tmp_path / "config.yaml").write_text("memory_max_share: 0.3\n")
    assert load_optimization_config(tmp_path / "config.yaml").memory_max_share == 0.3
    (tmp_path / "typo.json").write_text('{"memory_max_shar": 0.3}')
    with pytest.raises(ValueError):
        load_optimization_config(tmp_path / "typo.json")
    traces = tmp_path / "traces"
    traces.mkdir()
    for name in ("b", "a"):
        (traces / f"{name}.json").write_text(retrieval_run(name, [1]).model_dump_json())
    assert [r.run_id for r in load_traces([traces])] == ["a", "b"]
    (tmp_path / "empty").mkdir()
    with pytest.raises(ValueError, match="no trace"):
        load_traces([tmp_path / "empty"])
